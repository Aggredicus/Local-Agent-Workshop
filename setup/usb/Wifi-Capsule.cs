// Secrets stay in this process and the age child's stdin; never in argv or a plaintext USB file.
using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using System.Security;
using System.Text;
using System.Threading;

namespace LawUsb {
    [DataContract] public class WifiPayload {
        [DataMember] public int schema = 1;
        [DataMember] public string nonce;
        [DataMember] public string fingerprint;
        [DataMember] public string ssid;
        [DataMember] public string password;
    }
    public static class Capsule {
        private static string Reveal(SecureString secret) {
            IntPtr ptr = Marshal.SecureStringToBSTR(secret);
            try { return Marshal.PtrToStringBSTR(ptr); }
            finally { Marshal.ZeroFreeBSTR(ptr); }
        }
        public static void Export(string age, string recipient, string nonce, string fingerprint,
                                  string output, SecureString ssidInput, SecureString passwordInput, bool testWifi) {
            string ssid = Reveal(ssidInput), password = Reveal(passwordInput);
            if (Encoding.UTF8.GetByteCount(ssid) < 1 || Encoding.UTF8.GetByteCount(ssid) > 32 || ssid.IndexOfAny(new char[]{'\r','\n','\0'}) >= 0)
                throw new Exception("Network name must contain 1-32 UTF-8 bytes and no control characters.");
            if (password.Length < 8 || password.Length > 63) throw new Exception("WPA2 password must have 8-63 printable ASCII characters.");
            foreach(char c in password) if(c < 32 || c > 126) throw new Exception("Use a printable ASCII WPA2 password.");
            if (testWifi && !NativeWifi.Test(ssid, password)) throw new Exception("Windows did not verify authentication using the temporary profile; no capsule was exported.");
            if (File.Exists(output)) throw new Exception("Ciphertext output already exists; preserve it and choose another location.");
            WifiPayload payload = new WifiPayload { nonce=nonce, fingerprint=fingerprint, ssid=ssid, password=password };
            byte[] bytes;
            using (MemoryStream memory = new MemoryStream()) {
                new DataContractJsonSerializer(typeof(WifiPayload)).WriteObject(memory, payload);
                bytes = memory.ToArray();
            }
            ProcessStartInfo info = new ProcessStartInfo(age);
            // Recipient is validated by the PowerShell caller. Windows filenames cannot contain quotes.
            info.Arguments = "--encrypt -r " + recipient;
            info.UseShellExecute=false; info.CreateNoWindow=true;
            info.RedirectStandardInput=true; info.RedirectStandardError=true; info.RedirectStandardOutput=true;
            try {
                using (Process process = Process.Start(info)) {
                    process.StandardInput.BaseStream.Write(bytes, 0, bytes.Length);
                    process.StandardInput.Close();
                    if (!process.WaitForExit(20000)) { process.Kill(); throw new Exception("Encryption timed out."); }
                    if (process.ExitCode != 0) throw new Exception("Encryption failed; no plaintext diagnostic is emitted.");
                    using (MemoryStream encrypted = new MemoryStream()) {
                        process.StandardOutput.BaseStream.CopyTo(encrypted);
                        byte[] ciphertext = encrypted.ToArray();
                        // CreateNew never overwrites an operator file, even after a race.
                        using (FileStream file = new FileStream(output, FileMode.CreateNew, FileAccess.Write, FileShare.None)) {
                            file.Write(ciphertext, 0, ciphertext.Length); file.Flush();
                        }
                    }
                }
            } catch {
                throw new Exception("Encrypted export failed. Check the verified age binary and USB write permissions.");
            } finally {
                Array.Clear(bytes, 0, bytes.Length);
                payload.password=null; payload.ssid=null; password=null; ssid=null;
            }
        }
    }
    public static class NativeWifi {
        [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)] struct InterfaceInfo {
            public Guid id; [MarshalAs(UnmanagedType.ByValTStr, SizeConst=256)] public string description; public int state;
        }
        [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)] struct ConnectParams {
            public int mode; [MarshalAs(UnmanagedType.LPWStr)] public string profile;
            public IntPtr ssid, bssid; public int bssType; public uint flags;
        }
        [StructLayout(LayoutKind.Sequential)] struct Ssid {
            public uint length; [MarshalAs(UnmanagedType.ByValArray, SizeConst=32)] public byte[] bytes;
        }
        [StructLayout(LayoutKind.Sequential)] struct Association {
            public Ssid ssid; public int bssType;
            [MarshalAs(UnmanagedType.ByValArray, SizeConst=6)] public byte[] mac;
            public int phyType; public uint phyIndex, quality, rxRate, txRate;
        }
        [StructLayout(LayoutKind.Sequential)] struct Security { public int enabled, oneX, auth, cipher; }
        [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)] struct Connection {
            public int state, mode; [MarshalAs(UnmanagedType.ByValTStr, SizeConst=256)] public string profile;
            public Association association; public Security security;
        }
        [DllImport("wlanapi.dll")] static extern uint WlanOpenHandle(uint version, IntPtr reserved, out uint negotiated, out IntPtr handle);
        [DllImport("wlanapi.dll")] static extern uint WlanCloseHandle(IntPtr handle, IntPtr reserved);
        [DllImport("wlanapi.dll")] static extern uint WlanEnumInterfaces(IntPtr handle, IntPtr reserved, out IntPtr list);
        [DllImport("wlanapi.dll")] static extern void WlanFreeMemory(IntPtr ptr);
        [DllImport("wlanapi.dll")] static extern uint WlanConnect(IntPtr handle, ref Guid id, ref ConnectParams parameters, IntPtr reserved);
        [DllImport("wlanapi.dll")] static extern uint WlanDisconnect(IntPtr handle, ref Guid id, IntPtr reserved);
        [DllImport("wlanapi.dll")] static extern uint WlanQueryInterface(IntPtr handle, ref Guid id, int opcode, IntPtr reserved, out uint size, out IntPtr data, out int type);
        static Connection? Current(IntPtr handle, Guid id) {
            uint size; IntPtr data; int type;
            if (WlanQueryInterface(handle, ref id, 7, IntPtr.Zero, out size, out data, out type) != 0) return null;
            try { return (Connection)Marshal.PtrToStructure(data, typeof(Connection)); }
            finally { WlanFreeMemory(data); }
        }
        public static bool Test(string ssid, string password) {
            if (Environment.OSVersion.Platform != PlatformID.Win32NT) throw new Exception("Native Wi-Fi testing requires Windows.");
            uint negotiated; IntPtr handle;
            if (WlanOpenHandle(2, IntPtr.Zero, out negotiated, out handle) != 0) throw new Exception("Windows Wi-Fi service is unavailable.");
            try {
                IntPtr list;
                if (WlanEnumInterfaces(handle, IntPtr.Zero, out list) != 0) throw new Exception("Could not enumerate Wi-Fi adapters.");
                Guid id;
                try {
                    int count=Marshal.ReadInt32(list);
                    if (count != 1) throw new Exception("Exactly one Wi-Fi adapter is required for this optional test. Use Debian to test if none, or disable extra adapters yourself.");
                    id=((InterfaceInfo)Marshal.PtrToStructure(IntPtr.Add(list,8), typeof(InterfaceInfo))).id;
                } finally { WlanFreeMemory(list); }
                Connection? previous=Current(handle,id);
                if (previous.HasValue && previous.Value.state == 1 && previous.Value.mode != 0)
                    throw new Exception("Current Wi-Fi connection is temporary; restore a saved profile before testing.");
                string name="LAW-test-"+Guid.NewGuid().ToString("N");
                string xml="<?xml version=\"1.0\"?><WLANProfile xmlns=\"http://www.microsoft.com/networking/WLAN/profile/v1\"><name>"+name+"</name><SSIDConfig><SSID><hex>"+
                    BitConverter.ToString(Encoding.UTF8.GetBytes(ssid)).Replace("-","")+"</hex></SSID></SSIDConfig><connectionType>ESS</connectionType><connectionMode>manual</connectionMode><MSM><security><authEncryption><authentication>WPA2PSK</authentication><encryption>AES</encryption><useOneX>false</useOneX></authEncryption><sharedKey><keyType>passPhrase</keyType><protected>false</protected><keyMaterial>"+
                    SecurityElement.Escape(password)+"</keyMaterial></sharedKey></security></MSM></WLANProfile>";
                // Temporary profile: no WlanSetProfile and no plaintext XML file.
                ConnectParams parameters=new ConnectParams { mode=1, profile=xml, bssType=1 };
                try {
                    if (WlanConnect(handle,ref id,ref parameters,IntPtr.Zero)!=0) return false;
                    Stopwatch watch=Stopwatch.StartNew();
                    while(watch.ElapsedMilliseconds<30000) {
                        Connection? current=Current(handle,id);
                        if(current.HasValue && current.Value.state==1 && current.Value.mode==1 && current.Value.profile==name) {
                            string connected=Encoding.UTF8.GetString(current.Value.association.ssid.bytes,0,(int)current.Value.association.ssid.length);
                            if(connected==ssid) return true;
                        }
                        Thread.Sleep(400);
                    }
                    return false;
                } finally {
                    if(previous.HasValue && previous.Value.state==1 && !String.IsNullOrEmpty(previous.Value.profile)) {
                        ConnectParams restore=new ConnectParams { mode=0, profile=previous.Value.profile, bssType=1 };
                        if(WlanConnect(handle,ref id,ref restore,IntPtr.Zero)!=0) throw new Exception("Restore request failed. Reconnect using Windows network settings.");
                        Stopwatch restoredWatch=Stopwatch.StartNew(); bool restored=false;
                        while(restoredWatch.ElapsedMilliseconds<20000) {
                            Connection? restoredConnection=Current(handle,id);
                            if(restoredConnection.HasValue && restoredConnection.Value.state==1 && restoredConnection.Value.profile==previous.Value.profile) {restored=true;break;}
                            Thread.Sleep(400);
                        }
                        if(!restored) throw new Exception("Previous Wi-Fi profile did not reconnect; use Windows network settings.");
                    } else { WlanDisconnect(handle,ref id,IntPtr.Zero); }
                }
            } finally { WlanCloseHandle(handle,IntPtr.Zero); }
        }
    }
}
