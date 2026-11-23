import unittest
import numpy as np
from src.ghg import project_root,population_2021,population_2022,per_capita,population_sensitivity,aggregate_gross,gross_long,read_seeg

class PopulationTests(unittest.TestCase):
    def test_2021_source_and_sensitivity(self):
        root=project_root()
        pop=population_2021(root)
        self.assertEqual(pop.populacao.sum(),213317639)
        states=aggregate_gross(gross_long(read_seeg(root)))[1]
        a=per_capita(states,pop)
        b=per_capita(states,population_2022(root))
        np.testing.assert_allclose(a.set_index("Estado").Emissao.sort_index(),b.set_index("Estado").Emissao.sort_index())
        comparison=population_sensitivity(states,pop,population_2022(root))
        self.assertEqual(comparison.mudanca_posicao.ne(0).sum(),6)
        self.assertAlmostEqual(comparison.set_index("Estado").loc["RO","pc_2021"],75.9606996223,places=7)

if __name__ == "__main__": unittest.main()
