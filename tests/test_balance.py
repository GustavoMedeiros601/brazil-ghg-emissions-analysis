import unittest
import numpy as np
from src.ghg import project_root,read_seeg,gross_net,KIND,METRIC

class BalanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.raw=read_seeg(project_root())

    def test_balance_and_scope(self):
        national,states,categories=gross_net(self.raw)
        row=national.iloc[0]
        self.assertAlmostEqual(row.Brutas,2422625067.95982,places=4)
        self.assertAlmostEqual(row.Remocoes_assinadas,-666915168.0,places=4)
        self.assertAlmostEqual(row.Liquidas,row.Brutas+row.Remocoes_assinadas,places=4)
        np.testing.assert_allclose(states[["Brutas","Remocoes_assinadas","Liquidas"]].sum(),national[["Brutas","Remocoes_assinadas","Liquidas"]].iloc[0],rtol=1e-12)
        self.assertEqual(set(categories.loc[categories.Incluida_no_balanco,KIND]),{"Emissão","Remoção"})
        # Totais aproximadamente 2,4 Gt brutas e 1,76 Gt líquidas no relatório SEEG 10.
        self.assertAlmostEqual(row.Brutas/1e9,2.4,delta=.05)
        self.assertAlmostEqual(row.Liquidas/1e9,1.76,delta=.01)

    def test_reversed_removal_sign_is_rejected(self):
        changed=self.raw.copy()
        idx=changed.index[changed[KIND].eq("Remoção") & changed["Gás"].eq(METRIC) & changed[2021].lt(0)][0]
        changed.loc[idx,2021]*=-1
        with self.assertRaises(ValueError): gross_net(changed)

    def test_nci_and_bunker_do_not_change_balance(self):
        changed=self.raw.copy()
        excluded=~changed[KIND].isin(["Emissão","Remoção"])
        changed.loc[excluded,2021]=1e12
        before=gross_net(self.raw)[0]
        after=gross_net(changed)[0]
        np.testing.assert_allclose(before,after)

if __name__=="__main__": unittest.main()
