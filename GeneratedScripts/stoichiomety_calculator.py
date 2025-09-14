from rdkit import Chem
from rdkit.Chem import Descriptors
import pandas as pd

class StoichiometryCalculator:
    def __init__(self, reaction_file):
        self.reaction_file = reaction_file
        self.reactants = []
        self.products = []
        self.table = pd.DataFrame(columns=[
            'Compound', 'Formula', 'MW', 'Equivalents', 'Mass', 'Moles', 
            'Volume', 'Density', 'Molarity', 'Expected Mass', 'Obtained Mass', '% Yield'
        ])
        self.load_reaction()

    def load_reaction(self):
        try:
            with open(self.reaction_file, 'r') as file:
                mol_block = file.read()
            rxn = Chem.ReactionFromRxnBlock(mol_block)
            self.reactants = [mol for mol in rxn.GetReactants()]
            self.products = [mol for mol in rxn.GetProducts()]
            self.calculate_molecular_weights()
        except Exception as e:
            raise ValueError(f"Error loading reaction: {e}")

    def calculate_molecular_weights(self):
        for mol in self.reactants + self.products:
            formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
            mw = Descriptors.MolWt(mol)
            self.table = self.table.append({
                'Compound': mol.GetProp('_Name'),
                'Formula': formula,
                'MW': mw
            }, ignore_index=True)

    def update_table(self, compound_name, **kwargs):
        try:
            index = self.table[self.table['Compound'] == compound_name].index[0]
            for key, value in kwargs.items():
                self.table.at[index, key] = value
            self.calculate_stoichiometry(index)
        except IndexError:
            raise ValueError(f"Compound {compound_name} not found in the table.")
        except Exception as e:
            raise ValueError(f"Error updating table: {e}")

    def calculate_stoichiometry(self, index):
        try:
            row = self.table.iloc[index]
            mw = row['MW']
            if pd.notna(row['Mass']):
                self.table.at[index, 'Moles'] = row['Mass'] / mw
            if pd.notna(row['Moles']):
                self.table.at[index, 'Mass'] = row['Moles'] * mw
            # Additional calculations for Volume, Density, Molarity, etc.
            self.detect_limiting_reagent()
        except Exception as e:
            raise ValueError(f"Error in stoichiometry calculation: {e}")

    def detect_limiting_reagent(self):
        try:
            self.table['Moles'] = self.table['Moles'].astype(float)
            limiting_reagent = self.table.loc[self.table['Moles'].idxmin()]
            print(f"Limiting reagent: {limiting_reagent['Compound']}")
        except Exception as e:
            raise ValueError(f"Error detecting limiting reagent: {e}")

    def calculate_yield(self):
        try:
            for index, row in self.table.iterrows():
                if pd.notna(row['Obtained Mass']) and pd.notna(row['Expected Mass']):
                    self.table.at[index, '% Yield'] = (row['Obtained Mass'] / row['Expected Mass']) * 100
        except Exception as e:
            raise ValueError(f"Error calculating yield: {e}")

    def export_table(self, filename, file_format='csv'):
        try:
            if file_format == 'csv':
                self.table.to_csv(filename, index=False)
            elif file_format == 'pdf':
                # Placeholder for PDF export logic
                pass
            else:
                raise ValueError("Unsupported file format.")
        except Exception as e:
            raise ValueError(f"Error exporting table: {e}")

# Example usage:
# calculator = StoichiometryCalculator('reaction.rxn')
# calculator.update_table('C6H18BCl2NSi2', Mass=1.00, Equivalents=3)
# calculator.calculate_yield()
# calculator.export_table('stoichiometry.csv')