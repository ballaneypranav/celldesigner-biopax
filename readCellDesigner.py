
from lxml import objectify
from lxml import etree

def getSpeciesAliases(tree):
    """Returns species aliases used in a CellDesigner file."""

    speciesAliases = {}

    annotation = tree.model.annotation
    loSpeciesAliases = annotation.findall(
        './/celldesigner:listOfSpeciesAliases', namespaces=tree.nsmap)[0]

    for speciesAlias in loSpeciesAliases.getchildren():
        id = speciesAlias.get('id')
        species = speciesAlias.get('species')

        speciesAliases[id] = {
            'species': species
        }

    return speciesAliases


def getProteins(tree):
    """Returns Proteins used in the CellDesigner file."""

    proteins = {}

    annotation = tree.model.annotation
    loProteins = annotation.findall(
        './/celldesigner:listOfProteins', namespaces=tree.nsmap)[0]

    for protein in loProteins.getchildren():
        id = protein.get('id')
        name = protein.get('name')
        Type = protein.get('type')

        proteins[id] = {
            "name": name,
            "type": Type
        }

    return proteins


def getCompartments(tree):
    """Returns Compartments used in a CellDesigner file."""

    compartments = {}

    loCompartments = tree.findall('.//listOfCompartments', tree.nsmap)[0]

    for compartment in loCompartments.getchildren():
        metaid = compartment.get('metaid')
        id = compartment.get('id')

        compartments[id] = {
            'metaid': metaid
        }

    return compartments


def getSpecies(tree):
    """Returns Species used in a CellDesigner file."""

    species = {}

    loSpecies = tree.findall('.//listOfSpecies', tree.nsmap)[0]

    for sp in loSpecies.getchildren():
        metaid = sp.get('metaid')
        id = sp.get('id')
        name = sp.get('name')
        compartment = sp.get('compartment')
        Class = sp.findall('.//celldesigner:class', tree.nsmap)[0]

        species[id] = {
            'metaid': metaid,
            'name': name,
            'compartment': compartment,
            'class': Class
        }

        if Class == 'PROTEIN':
            proteinReference = sp.findall(
                './/celldesigner:proteinReference', tree.nsmap)[0]

            species[id]['proteinReference'] = proteinReference

    return species


def getReactions(tree):
    """Returns Reactions from a CellDesigner file."""

    reactions = {}

    loReactions = tree.findall('.//listOfReactions', tree.nsmap)[0]

    for rxn in loReactions.getchildren():
        metaid = rxn.get('metaid')
        id = rxn.get('id')
        reversible = rxn.get('reversible')
        fast = rxn.get('fast')
        reactionType = rxn.findall(
            './/celldesigner:reactionType', tree.nsmap)[0]

        loBaseReactants = rxn.findall(
            './/celldesigner:baseReactants', tree.nsmap)[0]
        baseReactants = {}

        for reactant in loBaseReactants.getchildren():
            species = reactant.get('species')
            alias = reactant.get('alias')

            baseReactants[alias] = {
                'species': species
            }

        loReactants = rxn.findall('.//listOfReactants', tree.nsmap)[0]
        reactants = {}

        for reactant in loReactants.getchildren():
            species = reactant.get('species')
            stoichiometry = reactant.get('stoichiometry')
            alias = reactant.findall(
                './/celldesigner:alias', tree.nsmap)[0].text

            reactants[alias] = {
                'species': species,
                'stoichiometry': stoichiometry
            }

        loBaseProducts = rxn.findall(
            './/celldesigner:baseProducts', tree.nsmap)[0]
        baseProducts = {}

        for product in loBaseProducts.getchildren():
            species = product.get('species')
            alias = product.get('alias')

            baseProducts[alias] = {
                'species': species
            }

        loProducts = rxn.findall('.//listOfProducts', tree.nsmap)[0]
        products = {}

        for product in loProducts.getchildren():
            species = product.get('species')
            stoichiometry = product.get('stoichiometry')
            alias = product.findall(
                './/celldesigner:alias', tree.nsmap)[0].text

            products[alias] = {
                'species': species,
                'stoichiometry': stoichiometry
            }

        connectPolicy = rxn.findall(
            './/celldesigner:connectScheme', tree.nsmap)[0].get('connectPolicy')

        reactions[id] = {
            'metaid': metaid,
            'reversible': reversible,
            'fast': fast,
            'reactionType': reactionType,
            'baseReactants': baseReactants,
            'baseProducts': baseProducts,
            'reactants': reactants,
            'products': products,
            'connectPolicy': connectPolicy
        }

    return reactions
