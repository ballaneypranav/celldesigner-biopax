from lxml import objectify
from lxml import etree
from pprint import pprint

BP  = 'http://www.biopax.org/release/biopax-level3.owl#'
OWL = 'http://www.w3.org/2002/07/owl#'
RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'

def main():

    with open('sim1.xml', 'rb') as file:
        tree = objectify.fromstring(file.read())

    cache = {}
    cache['speciesAliases'] = getSpeciesAliases(tree)
    cache['proteins'] = getProteins(tree)
    cache['compartments'] = getCompartments(tree)
    cache['species'] = getSpecies(tree)
    cache['reactions'] = getReactions(tree)

    pprint(cache)

    owl = getOwlModel()

    addCellularLocationVocabularies(owl, cache)
    addProteins(owl, cache)

    owl_string = str(etree.tostring(owl, pretty_print=True), encoding='UTF8')
    print(owl_string)

    with open('sim1-converted.owl', 'w') as file:
        file.write(owl_string)


def getSpeciesAliases(tree):

    speciesAliases = {}

    annotation = tree.model.annotation
    loSpeciesAliases = annotation.findall('.//celldesigner:listOfSpeciesAliases', namespaces=tree.nsmap)[0]

    for speciesAlias in loSpeciesAliases.getchildren():
        id = speciesAlias.get('id')
        species = speciesAlias.get('species')

        speciesAliases[id] = {
            'species': species
        }

    return speciesAliases

def getProteins(tree):
    proteins = {}

    annotation = tree.model.annotation
    loProteins = annotation.findall('.//celldesigner:listOfProteins', namespaces=tree.nsmap)[0]

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
            proteinReference = sp.findall('.//celldesigner:proteinReference', tree.nsmap)[0]
        
            species[id]['proteinReference'] = proteinReference

    return species

def getReactions(tree):

    reactions = {}

    loReactions = tree.findall('.//listOfReactions', tree.nsmap)[0]

    for rxn in loReactions.getchildren():
        metaid = rxn.get('metaid')
        id = rxn.get('id')
        reversible = rxn.get('reversible')
        fast = rxn.get('fast')
        reactionType = rxn.findall('.//celldesigner:reactionType', tree.nsmap)[0]

        loBaseReactants = rxn.findall('.//celldesigner:baseReactants', tree.nsmap)[0]
        baseReactants = []

        for reactant in loBaseReactants.getchildren():
            baseReactants.append({
                'species': reactant.get('species'),
                'alias': reactant.get('alias')
            })

        loBaseProducts = rxn.findall('.//celldesigner:baseProducts', tree.nsmap)[0]
        baseProducts = []

        for product in loBaseProducts.getchildren():
            baseProducts.append({
                'species': product.get('species'),
                'alias': product.get('alias')
            })

        connectPolicy = rxn.findall('.//celldesigner:connectScheme', tree.nsmap)[0].get('connectPolicy')
        
        reactions[id] = {
            'metaid': metaid,
            'reversible': reversible,
            'fast': fast,
            'reactionType': reactionType,
            'baseReactants': baseReactants,
            'baseProducts': baseProducts,
            'connectPolicy': connectPolicy
        }

    return reactions

def getElement(name, namespace):
    return etree.Element('{' + namespace + '}' + name)

def getOwlModel():
    owl_nsmap = {
        None  : 'http://www.pantherdb.org/pathways/biopax#',
        'rdf' : RDF,
        'owl' : OWL,
        'xsd' : 'http://www.w3.org/2001/XMLSchema#',
        'bp'  : BP
    }

    owl = etree.Element("RDF", nsmap = owl_nsmap)
    owl.tag = '{' + RDF + '}RDF'

    ontology = getElement('Ontology', OWL)

    owl.append(ontology)
    imports = getElement('imports', OWL)
    imports.set("{%s}resource" % RDF, BP)
    ontology.append(imports)

    return owl

def addCellularLocationVocabularies(owl, cache):
    compartments = cache['compartments']

    for key, value in compartments.items():
        cellularLocationVocabulary = getElement('CellularLocationVocabulary', BP)
        cellularLocationVocabulary.set("{%s}ID" % RDF, key)

        owl.append(cellularLocationVocabulary)

def addProteins(owl, cache):

    for proteinReference, desc in cache['proteins'].items():

        # consolidate protein data from cache
        for sp in cache['species']:
            if cache['species'][sp]['proteinReference'] == proteinReference:
                desc['speciesID'] = sp
                desc['compartment'] = cache['species'][sp]['compartment']
                break
        for alias in cache['speciesAliases']:
            if cache['speciesAliases'][alias]['species'] == desc['speciesID']:
                desc['speciesAliasID'] = alias
                break

        desc['rdf:ID'] = desc['name'] + '_' + desc['speciesID'] + '_' + desc['speciesAliasID']

        protein = getElement('Protein', BP)
        protein.set("{%s}ID" % RDF, desc['rdf:ID'])

        displayName = getElement('displayName', BP)
        displayName.text = cache['proteins'][proteinReference]['name']
        displayName.set("{%s}datatype" % RDF, "xsd:string")
        protein.append(displayName)

        standardName = getElement('standardName', BP)
        standardName.text = cache['proteins'][proteinReference]['name']
        standardName.set("{%s}datatype" % RDF, "xsd:string")
        protein.append(standardName)

        cellularLocation = getElement('cellularLocation', BP)
        cellularLocation.set("{%s}resource" % RDF, '#' + desc['compartment'])
        protein.append(cellularLocation)

        owl.append(protein)

main()