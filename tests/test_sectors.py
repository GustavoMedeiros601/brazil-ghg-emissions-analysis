import unittest
import numpy as np
from src.ghg import project_root,read_seeg,gross_long,state_sector,temporal_decomposition,aggregate_gross

class SectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.long=gross_long(read_seeg(project_root()))

    def test_state_components_reconcile(self):
        frame=state_sector(self.long)
        self.assertEqual(len(frame),135)
        self.assertEqual(frame.Emissao.isna().sum(),3)
        self.assertEqual(set(frame.loc[frame.Emissao.isna(),"Estado"]),{"AC","AP","RR"})
        np.testing.assert_allclose(frame.groupby("Estado").Participacao_pct.sum(),100)
        expected=aggregate_gross(self.long)[1].set_index("Estado").Emissao.sort_index()
        np.testing.assert_allclose(frame.groupby("Estado").Emissao.sum().sort_index(),expected)

    def test_historical_deltas_reconcile_with_national_change(self):
        annual=aggregate_gross(self.long)[0].set_index("Ano").Emissao
        frame=temporal_decomposition(self.long)
        for (start,end),part in frame.groupby(["Ano_inicial","Ano_final"]):
            self.assertAlmostEqual(part.Diferenca.sum(),annual[end]-annual[start],places=4)
            self.assertAlmostEqual(part.Contribuicao_pp.sum(),(annual[end]/annual[start]-1)*100,places=9)
        with self.assertRaises(ValueError): temporal_decomposition(self.long,[(1989,1990)])

if __name__=="__main__": unittest.main()
