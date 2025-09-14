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
        self.parse_reaction()

    def parse_reaction(self):
        # Load reaction file and parse reactants and products
        if self.reaction_file.endswith('.mol') or self.reaction_file.endswith('.rxn'):
            self._parse_mol_rxn()
        else:
            raise ValueError("Unsupported file format")
        self.calculate_molecular_weights()

    def _parse_mol_rxn(self):
        # Placeholder for parsing logic
        pass

    def calculate_molecular_weights(self):
        for compound in self.reactants + self.products:
            mol = Chem.MolFromSmiles(compound)
            mw = Descriptors.MolWt(mol)
            self.table = self.table.append({'Compound': compound, 'MW': mw}, ignore_index=True)

    def update_table(self, compound, field, value):
        # Update the table with new values and recalculate dependent fields
        self.table.loc[self.table['Compound'] == compound, field] = value
        self.recalculate(compound)

    def recalculate(self, compound):
        # Recalculate moles, mass, volume, etc. based on updated values
        row = self.table[self.table['Compound'] == compound]
        mw = row['MW'].values[0]
        mass = row['Mass'].values[0]
        moles = mass / mw if mw else None
        self.table.loc[self.table['Compound'] == compound, 'Moles'] = moles
        # Further calculations...

    def identify_limiting_reagent(self):
        # Identify the limiting reagent based on moles/equivalents
        pass

    def calculate_yield(self):
        # Calculate the yield based on expected and obtained mass
        for index, row in self.table.iterrows():
            if row['Expected Mass'] and row['Obtained Mass']:
                yield_percent = (row['Obtained Mass'] / row['Expected Mass']) * 100
                self.table.at[index, '% Yield'] = yield_percent

    def export_table(self, file_format='csv'):
        if file_format == 'csv':
            self.table.to_csv('stoichiometry_table.csv', index=False)
        elif file_format == 'pdf':
            # PDF export logic
            pass
        else:
            raise ValueError("Unsupported export format")

    def validate_data(self):
        # Validate data for inconsistencies
        for index, row in self.table.iterrows():
            if row['Mass'] < 0 or row['Moles'] < 0:
                raise ValueError("Negative values are not allowed")

# Example usage
# calculator = StoichiometryCalculator('reaction.mol')
# calculator.update_table('C6H18BCl2NSi2', 'Mass', 1.00)
# calculator.calculate_yield()
# calculator.export_table('csv')