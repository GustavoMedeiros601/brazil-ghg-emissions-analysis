"""Compara os arquivos consumidos pela exploração com seus cálculos na fonte."""
import hashlib
import json
import unittest
import pandas as pd
from src.ghg import (
    project_root, read_seeg, gross_long, aggregate_gross, state_sector,
    temporal_decomposition, gross_net, population_2021, population_2022,
    population_sensitivity, per_capita,
)


class ExportTests(unittest.TestCase):
    def test_exported_tables_match_source(self):
        root = project_root()
        raw = read_seeg(root)
        long = gross_long(raw)
        states = aggregate_gross(long)[1]
        national, uf_balance, categories = gross_net(raw)
        expected = {
            "emissao_per_capita_2021.csv": per_capita(states, population_2021(root)),
            "sensibilidade_per_capita_2021.csv": population_sensitivity(states, population_2021(root), population_2022(root)),
            "emissao_uf_setor_2021.csv": state_sector(long),
            "decomposicao_setorial_historica.csv": temporal_decomposition(long),
            "balanco_nacional_2021.csv": national,
            "balanco_uf_2021.csv": uf_balance,
            "categorias_seeg_2021.csv": categories,
        }
        for name, frame in expected.items():
            with self.subTest(file=name):
                actual = pd.read_csv(root / "data/processed" / name)
                expected_frame = frame.reset_index(drop=True).rename_axis(columns=None)
                pd.testing.assert_frame_equal(actual, expected_frame, check_dtype=False, rtol=1e-12, atol=1e-6)

    def test_source_checksums(self):
        root = project_root()
        for source in json.loads((root / "docs/sources.json").read_text(encoding="utf-8")).values():
            self.assertEqual(hashlib.sha256((root / source["path"]).read_bytes()).hexdigest(), source["sha256"])


if __name__ == "__main__":
    unittest.main()
