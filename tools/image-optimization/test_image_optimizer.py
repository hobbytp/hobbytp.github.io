import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path


pil = types.ModuleType("PIL")
pil.Image = object()
sys.modules.setdefault("PIL", pil)

module_path = Path(__file__).with_name("image_optimizer.py")
spec = importlib.util.spec_from_file_location("image_optimizer", module_path)
image_optimizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(image_optimizer)


class ImageOptimizerTest(unittest.TestCase):
    def test_files_below_output_directory_are_not_reprocessed(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_dir = Path(tmp_dir) / "images"
            output_dir = input_dir / "optimized"
            source = input_dir / "generated-covers" / "cover.png"
            recursive_output = output_dir / "generated-covers" / "cover_320w.webp"
            source.parent.mkdir(parents=True)
            recursive_output.parent.mkdir(parents=True)
            source.write_bytes(b"source")
            recursive_output.write_bytes(b"generated")

            optimizer = image_optimizer.ImageOptimizer(
                input_dir=str(input_dir),
                output_dir=str(output_dir),
                backup=True,
            )
            backup_output = optimizer.backup_dir / "generated-covers" / "cover.png"
            backup_output.parent.mkdir(parents=True)
            backup_output.write_bytes(b"backup")

            self.assertTrue(optimizer.should_process_file(source))
            self.assertFalse(optimizer.should_process_file(recursive_output))
            self.assertFalse(optimizer.should_process_file(backup_output))


if __name__ == "__main__":
    unittest.main()
