import pytest

from workshop.usb.bundle import USBError, build_bundle
from workshop.usb.media import pack


def test_builder_rejects_unpinned_images_before_docker(tmp_path):
    with pytest.raises(USBError, match='pinned'):
        build_bundle(tmp_path, tmp_path / 'out', 'debian:latest')
    assert not (tmp_path / 'out').exists()


def test_packer_rejects_wrong_age_archive(tmp_path):
    archive = tmp_path / 'age.zip'
    archive.write_bytes(b'tampered executable distribution')
    with pytest.raises(USBError, match='digest'):
        pack(tmp_path, tmp_path, archive, tmp_path / 'output.zip')
    assert not (tmp_path / 'output.zip').exists()


def test_packer_never_overwrites_existing_output(tmp_path):
    output = tmp_path / 'output.zip'
    output.write_bytes(b'operator data')
    with pytest.raises(USBError, match='exists'):
        pack(tmp_path, tmp_path, tmp_path / 'missing.zip', output)
    assert output.read_bytes() == b'operator data'
