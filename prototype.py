"""
A basic prototype for a CellDesigner to BioPAX Converter.
"""
from lxml import objectify
from lxml import etree
from readCellDesigner import *
from writeBioPAX import *

def main():

    with open('input.xml', 'rb') as file:
        tree = objectify.fromstring(file.read())

    # Read the CellDesigner file and build a cache
    cache = {}
    cache['speciesAliases'] = getSpeciesAliases(tree)
    cache['proteins'] = getProteins(tree)
    cache['compartments'] = getCompartments(tree)
    cache['species'] = getSpecies(tree)
    cache['reactions'] = getReactions(tree)
    cache['vocabularies'] = {
        'RelationshipTypes': {},
        'Interactions': {}
    }

    # pprint(cache)

    # Build a new BioPAX model
    owl = getOwlModel()

    # Add components
    addCellularLocationVocabularies(owl, cache)
    addProteins(owl, cache)
    addSmallMolecules(owl, cache)
    processReactions(owl, cache)

    # Write to file
    owl_string = str(etree.tostring(owl, pretty_print=True), encoding='UTF8')
    # print(owl_string)

    with open('output.owl', 'w') as file:
        file.write(owl_string)

if __name__ == "__main__":
    main()