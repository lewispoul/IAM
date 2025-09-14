import unittest
from unittest.mock import patch, mock_open
from stoichiometry_calculator import StoichiometryCalculator
import pandas as pd

class TestStoichiometryCalculator(unittest.TestCase):

    def setUp(self):
        # Mock reaction file content
        self.mock_rxn_content = """
        $RXN

          RDKit

        2  1
        $MOL
        -ISIS-  08282017242D

          6  5  0  0  0  0            999 V2000
           -0.7500    0.0000    0.0000 C   0  0  0  0  0  0
           -0.7500    1.5000    0.0000 C   0  0  0  0  0  0
           -2.2500    1.5000    0.0000 C   0  0  0  0  0  0
           -3.0000    0.0000    0.0000 C   0  0  0  0  0  0
           -2.2500   -1.5000    0.0000 C   0  0  0  0  0  0
           -0.7500   -1.5000    0.0000 C   0  0  0  0  0  0
          1  2  1  0
          2  3  1  0
          3  4  1  0
          4  5  1  0
          5  6  1  0
        M  END
        $MOL
        -ISIS-  08282017242D

          6  5  0  0  0  0            999 V2000
           -0.7500    0.0000    0.0000 C   0  0  0  0  0  0
           -0.7500    1.5000    0.0000 C   0  0  0  0  0  0
           -2.2500    1.5000    0.0000 C   0  0  0  0  0  0
           -3.0000    0.0000    0.0000 C   0  0  0  0  0  0
           -2.2500   -1.5000    0.0000 C   0  0  0  0  0  0
           -0.7500   -1.5000    0.0000 C   0  0  0  0  0  0
          1  2  1  0
          2  3  1  0
          3  4  1  0
          4  5  1  0
          5  6  1  0
        M  END
        """
        self.mock_open = mock_open(read_data=self.mock_rxn_content)

    @patch('builtins.open', new_callable=mock_open, read_data="mock_rxn_content")
    def test_load_reaction(self, mock_file):
        calculator = StoichiometryCalculator('mock_reaction.rxn')
        self.assertEqual(len(calculator.reactants), 1)
        self.assertEqual(len(calculator.products), 1)

    @patch('builtins.open', new_callable=mock_open, read_data="mock_rxn_content")
    def test_calculate_molecular_weights(self, mock_file):
        calculator = StoichiometryCalculator('mock_reaction.rxn')
        calculator.calculate_molecular_weights()
        self.assertFalse(calculator.table.empty)
        self.assertIn('MW', calculator.table.columns)

    @patch('builtins.open', new_callable=mock_open, read_data="mock_rxn_content")
    def test_update_table(self, mock_file):
        calculator = StoichiometryCalculator('mock_reaction.rxn')
        calculator.update_table('C6H6', Mass=78.11)
        self.assertEqual(calculator.table.loc[0, 'Mass'], 78.11)

    @patch('builtins.open', new_callable=mock_open, read_data="mock_rxn_content")
    def test_calculate_stoichiometry(self, mock_file):
        calculator = StoichiometryCalculator('mock_reaction.rxn')
        calculator.update_table('C6H6', Mass=78.11)
        self.assertAlmostEqual(calculator.table.loc[0, 'Moles'], 1.0, places=2)

    @patch('builtins.open', new_callable=mock_open, read_data="mock_rxn_content")
    def test_detect_limiting_reagent(self, mock_file):
        calculator = StoichiometryCalculator('mock_reaction.rxn')
        calculator.update_table('C6H6', Mass=78.11)
        calculator.detect_limiting_reagent()
        self.assertEqual(calculator.table.loc[0, 'Compound'], 'C6H6')

    @patch('builtins.open', new_callable=mock_open, read_data="mock_rxn_content")
    def test_calculate_yield(self, mock_file):
        calculator = StoichiometryCalculator('mock_reaction.rxn')
        calculator.update_table('C6H6', Mass=78.11, ExpectedMass=78.11, ObtainedMass=70.0)
        calculator.calculate_yield()
        self.assertAlmostEqual(calculator.table.loc[0, '% Yield'], 89.57, places=2)

    @patch('builtins.open', new_callable=mock_open, read_data="mock_rxn_content")
    def test_export_table(self, mock_file):
        calculator = StoichiometryCalculator('mock_reaction.rxn')
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            calculator.export_table('stoichiometry.csv')
            mock_to_csv.assert_called_once_with('stoichiometry.csv', index=False)

    @patch('builtins.open', new_callable=mock_open, read_data="mock_rxn_content")
    def test_invalid_file_format(self, mock_file):
        calculator = StoichiometryCalculator('mock_reaction.rxn')
        with self.assertRaises(ValueError):
            calculator.export_table('stoichiometry.txt', file_format='txt')

if __name__ == '__main__':
    unittest.main()