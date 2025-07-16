import unittest
from unittest.mock import patch, MagicMock
from stoichiometry_calculator import StoichiometryCalculator
import pandas as pd

class TestStoichiometryCalculator(unittest.TestCase):

    @patch('stoichiometry_calculator.Chem.MolFromSmiles')
    @patch('stoichiometry_calculator.Descriptors.MolWt')
    def setUp(self, mock_MolWt, mock_MolFromSmiles):
        # Mock RDKit functions
        mock_MolFromSmiles.return_value = MagicMock()
        mock_MolWt.return_value = 100.0

        # Create a test instance with a mock reaction file
        self.calculator = StoichiometryCalculator('test_reaction.mol')
        self.calculator.reactants = ['C6H6', 'O2']
        self.calculator.products = ['CO2', 'H2O']
        self.calculator.calculate_molecular_weights()

    def test_parse_reaction_unsupported_format(self):
        with self.assertRaises(ValueError):
            StoichiometryCalculator('reaction.txt')

    def test_calculate_molecular_weights(self):
        self.assertEqual(len(self.calculator.table), 4)
        self.assertTrue(all(self.calculator.table['MW'] == 100.0))

    def test_update_table_and_recalculate(self):
        self.calculator.update_table('C6H6', 'Mass', 78.0)
        benzene_row = self.calculator.table[self.calculator.table['Compound'] == 'C6H6']
        self.assertAlmostEqual(benzene_row['Moles'].values[0], 0.78)

    def test_calculate_yield(self):
        self.calculator.table = pd.DataFrame({
            'Compound': ['CO2'],
            'Expected Mass': [44.0],
            'Obtained Mass': [40.0]
        })
        self.calculator.calculate_yield()
        self.assertAlmostEqual(self.calculator.table['% Yield'].values[0], 90.91, places=2)

    def test_export_table_unsupported_format(self):
        with self.assertRaises(ValueError):
            self.calculator.export_table('xml')

    def test_validate_data_negative_values(self):
        self.calculator.table = pd.DataFrame({
            'Compound': ['C6H6'],
            'Mass': [-1.0],
            'Moles': [0.0]
        })
        with self.assertRaises(ValueError):
            self.calculator.validate_data()

    def test_export_table_csv(self):
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            self.calculator.export_table('csv')
            mock_to_csv.assert_called_once_with('stoichiometry_table.csv', index=False)

if __name__ == '__main__':
    unittest.main()