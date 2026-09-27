from __future__ import annotations

import hashlib
import json
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "profile" / "mascot-motion" / "manifest.json"


def _gif_frames_and_delays(data: bytes) -> tuple[int, list[int]]:
    if data[:6] not in (b"GIF87a", b"GIF89a"):
        raise ValueError("cabecera GIF inválida")
    if struct.unpack_from("<HH", data, 6) != (128, 128):
        raise ValueError("dimensiones GIF distintas a 128x128")
    packed = data[10]
    offset = 13 + (3 * (2 ** ((packed & 0x07) + 1)) if packed & 0x80 else 0)
    delays: list[int] = []

    def skip_sub_blocks(index: int) -> int:
        while True:
            length = data[index]
            index += 1
            if length == 0:
                return index
            index += length

    while offset < len(data):
        marker = data[offset]
        offset += 1
        if marker == 0x3B:
            break
        if marker == 0x21:
            label = data[offset]
            offset += 1
            if label == 0xF9:
                block_length = data[offset]
                if block_length != 4:
                    raise ValueError("bloque de control GIF inválido")
                delays.append(struct.unpack_from("<H", data, offset + 2)[0])
            offset = skip_sub_blocks(offset)
            continue
        if marker != 0x2C:
            raise ValueError(f"bloque GIF inesperado: {marker:#x}")
        image_packed = data[offset + 8]
        offset += 9
        if image_packed & 0x80:
            offset += 3 * (2 ** ((image_packed & 0x07) + 1))
        offset += 1  # LZW minimum code size
        offset = skip_sub_blocks(offset)
    return len(delays), delays


class MascotMotionAssetTests(unittest.TestCase):
    def test_motion_files_match_manifest_dimensions_hash_and_frame_rate(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        records = manifest["records"]
        self.assertEqual(manifest["minimumFps"], 25)
        self.assertEqual(len(records), 6)
        self.assertEqual({item["variant"] for item in records}, {"female", "male", "neutral"})
        self.assertEqual({item["state"] for item in records}, {"exercise", "rest"})
        for record in records:
            with self.subTest(gif=record["gif"]):
                gif_path = ROOT / record["gif"]
                still_path = ROOT / record["still"]
                gif = gif_path.read_bytes()
                still = still_path.read_bytes()
                self.assertEqual(gif_path.stat().st_size, record["gifBytes"])
                self.assertEqual(hashlib.sha256(gif).hexdigest(), record["sha256"])
                self.assertEqual(gif[:4], b"GIF8")
                self.assertEqual(struct.unpack_from("<HH", gif, 6), (128, 128))
                self.assertEqual(still[:4], b"RIFF")
                self.assertEqual(still[8:12], b"WEBP")
                self.assertEqual(int.from_bytes(still[24:27], "little") + 1, 128)
                self.assertEqual(int.from_bytes(still[27:30], "little") + 1, 128)
                frames, delays_cs = _gif_frames_and_delays(gif)
                self.assertEqual(frames, record["frames"])
                self.assertEqual(len(delays_cs), frames)
                self.assertTrue(all(delay_cs == 4 for delay_cs in delays_cs))
                self.assertEqual(record["frameDurationMs"], 40)


if __name__ == "__main__":
    unittest.main()
