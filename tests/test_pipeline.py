import unittest
import pandas as pd
from src.ghg import per_capita, population_2022, aggregate_gross, gross_long, read_seeg, project_root, validate_processed

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = project_root()
        cls.long = gross_long(read_seeg(cls.root))

    def test_raw_and_published_totals_reconcile(self):
        annual, states, sectors, allocation = aggregate_gross(self.long)
        for actual, filename in [(annual,"emissao_anual_brasil.csv"),(states,"emissao_estado_2021.csv"),(sectors,"emissao_setor_2021.csv")]:
            expected = pd.read_csv(self.root / "data/processed" / filename)
            pd.testing.assert_frame_equal(actual.reset_index(drop=True),expected,check_dtype=False,rtol=1e-12,atol=1e-6)
        self.assertGreater(allocation.loc[allocation.Alocacao.eq("Sem alocação estadual"),"Emissao"].iloc[0],0)

    def test_missing_or_duplicated_population_is_rejected(self):
        states = aggregate_gross(self.long)[1]
        pop = population_2022(self.root)
        for invalid in [pop.iloc[1:],pd.concat([pop,pop.iloc[:1]])]:
            with self.assertRaises(ValueError): per_capita(states, invalid)

    def test_published_contract(self):
        self.assertEqual(validate_processed(self.root)["ufs"], 27)

if __name__ == "__main__": unittest.main()
