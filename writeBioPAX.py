from lxml import objectify
from lxml import etree

BP = 'http://www.biopax.org/release/biopax-level3.owl#'
OWL = 'http://www.w3.org/2002/07/owl#'
RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'

def getElement(name, namespace):
    """Creates and returns a new BioPAX element."""
    return etree.Element('{' + namespace + '}' + name)


def addAttr(element, namespace, attr, value):
    """Adds an attribute to the specified BioPAX element."""

    element.set('{' + namespace + '}' + attr, value)


def getOwlModel():
    """Returns a new BioPAX model."""

    owl_nsmap = {
        None: 'http://www.pantherdb.org/pathways/biopax#',
        'rdf': RDF,
        'owl': OWL,
        'xsd': 'http://www.w3.org/2001/XMLSchema#',
        'bp': BP
    }

    owl = etree.Element("RDF", nsmap=owl_nsmap)
    owl.tag = '{' + RDF + '}RDF'

    ontology = getElement('Ontology', OWL)

    owl.append(ontology)
    imports = getElement('imports', OWL)
    addAttr(imports, RDF, 'resource', BP)
    ontology.append(imports)

    return owl


def addCellularLocationVocabularies(owl, cache):
    """Add cellularlocations from compartments."""

    compartments = cache['compartments']

    for key, value in compartments.items():
        cellularLocationVocabulary = getElement(
            'CellularLocationVocabulary', BP)
        addAttr(cellularLocationVocabulary, RDF, 'ID', key)

        owl.append(cellularLocationVocabulary)


def addProteins(owl, cache):
    """Add Proteins to a BioPAX model."""

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

        protein = getElement('Protein', BP)
        addAttr(protein, RDF, 'ID', desc['speciesAliasID'])

        displayName = getElement('displayName', BP)
        displayName.text = cache['proteins'][proteinReference]['name']
        addAttr(displayName, RDF, 'datatype', 'xsd:string')
        protein.append(displayName)

        standardName = getElement('standardName', BP)
        standardName.text = cache['proteins'][proteinReference]['name']
        addAttr(standardName, RDF, 'datatype', 'xsd:string')
        protein.append(standardName)

        cellularLocation = getElement('cellularLocation', BP)
        addAttr(cellularLocation, RDF, 'resource', desc['compartment'])
        protein.append(cellularLocation)

        owl.append(protein)


def addSmallMolecules(owl, cache):
    """Add SmallMolecules to a BioPAX model."""

    for spID, spDesc in cache['species'].items():
        if spDesc['class'] == 'SIMPLE_MOLECULE':

            # consolidate data from cache
            for aliasID, aliasDesc in cache['speciesAliases'].items():
                if aliasDesc['species'] == spID:
                    spDesc['speciesAliasID'] = aliasID
                    break

            SmallMolecule = getElement('SmallMolecule', BP)
            addAttr(SmallMolecule, RDF, 'ID', spDesc['speciesAliasID'])

            displayName = getElement('displayName', BP)
            addAttr(displayName, RDF, 'datatype', 'xsd:string')
            displayName.text = spDesc['name']
            SmallMolecule.append(displayName)

            standardName = getElement('standardName', BP)
            addAttr(standardName, RDF, 'datatype', 'xsd:string')
            standardName.text = spDesc['name']
            SmallMolecule.append(standardName)

            cellularLocation = getElement('cellularLocation', BP)
            addAttr(cellularLocation, RDF, 'resource',
                    '#' + spDesc['compartment'])
            SmallMolecule.append(cellularLocation)

            owl.append(SmallMolecule)


def processReactions(owl, cache):
    """
    Go through reactions in the cache and add relevant 
    InteractionTypes, Stoichiometries
    and reactions to the BioPAX model.
    """

    for rxnID, rxnDesc in cache['reactions'].items():

        # add Interaction to vocab if not present
        if rxnDesc['reactionType'] not in cache['vocabularies']['Interactions'].keys():
            InteractionVocabulary = getElement('InteractionVocabulary', BP)
            addAttr(InteractionVocabulary, RDF, 'about',
                    'CELLDESIGNER_INTERACTION_VOCABULARY=' + rxnDesc['reactionType'])

            term = getElement('term', BP)
            addAttr(term, RDF, 'datatype', 'xsd:string')
            term.text = str(rxnDesc['reactionType'])
            InteractionVocabulary.append(term)

            owl.append(InteractionVocabulary)
            cache['vocabularies']['Interactions'][rxnDesc['reactionType']] = {
                'rdf:about': 'CELLDESIGNER_INTERACTION_VOCABULARY=' + rxnDesc['reactionType'],
                'term': rxnDesc['reactionType']
            }

        # add reaction
        BiochemicalReaction = getElement('BiochemicalReaction', BP)
        addAttr(BiochemicalReaction, RDF, 'ID', rxnID)

        # left
        reactantID = list(rxnDesc['reactants'].keys())[0]
        left = getElement('left', BP)
        addAttr(left, RDF, 'resource', '#' + reactantID)
        BiochemicalReaction.append(left)

        # right
        productID = list(rxnDesc['products'].keys())[0]
        right = getElement('right', BP)
        addAttr(right, RDF, 'resource', '#' + productID)
        BiochemicalReaction.append(right)

        # standardName
        standardName = getElement('standardName', BP)
        addAttr(standardName, RDF, 'datatype', 'xsd:string')
        standardName.text = rxnID
        BiochemicalReaction.append(standardName)

        # interactionType
        interactionType = getElement('interactionType', BP)
        addAttr(interactionType, RDF, 'resource',
                'CELLDESIGNER_INTERACTION_VOCABULARY=' + rxnDesc['reactionType'])
        BiochemicalReaction.append(interactionType)

        # conversionDirection
        conversionDirection = getElement('conversionDirection', BP)
        addAttr(conversionDirection, RDF, 'datatype', 'xsd:string')
        if rxnDesc['reversible'] == 'false':
            conversionDirection.text = 'LEFT_TO_RIGHT'
        else:
            conversionDirection.text = 'REVERSIBLE'
        BiochemicalReaction.append(conversionDirection)

        # stoichiometries
        addStoichiometries(owl, cache, rxnID)

        reactantPartSty = getElement('participantStoichiometry', BP)
        addAttr(reactantPartSty, RDF, 'resource', '#' +
                'PARTICIPANT_STOICHIOMETRY_' + rxnID + '_1')
        BiochemicalReaction.append(reactantPartSty)

        productPartSty = getElement('participantStoichiometry', BP)
        addAttr(productPartSty, RDF, 'resource', '#' +
                'PARTICIPANT_STOICHIOMETRY_' + rxnID + '_2')
        BiochemicalReaction.append(productPartSty)

        owl.append(BiochemicalReaction)


def addStoichiometries(owl, cache, rxnID):
    """Adds stoichiometries from a reaction to a BioPAX model."""
    rxnDesc = cache['reactions'][rxnID]
    reactantID = list(rxnDesc['reactants'].keys())[0]
    productID = list(rxnDesc['products'].keys())[0]

    # reactant stoichiometry
    reactantSty = getElement('Stoichiometry', BP)
    addAttr(reactantSty, RDF, 'ID', 'PARTICIPANT_STOICHIOMETRY_' + rxnID + '_1')

    reactantEntity = getElement('physicalEntity', BP)
    addAttr(reactantEntity, RDF, 'resource', '#' + reactantID)
    reactantSty.append(reactantEntity)

    reactantStyCoeff = getElement('stoichiometricCoefficient', BP)
    addAttr(reactantStyCoeff, BP, 'datatype', 'xsd:float')
    reactantStyValue = rxnDesc['reactants'][reactantID]['stoichiometry']
    if reactantStyValue is None:
        reactantStyCoeff.text = '1.0'
    else:
        reactantStyCoeff.text = reactantStyValue

    reactantSty.append(reactantStyCoeff)
    owl.append(reactantSty)

    # product stoichiometry
    productSty = getElement('Stoichiometry', BP)
    addAttr(productSty, RDF, 'ID', 'PARTICIPANT_STOICHIOMETRY_' + rxnID + '_2')

    productEntity = getElement('physicalEntity', BP)
    addAttr(productEntity, RDF, 'resource', '#' + productID)
    productSty.append(productEntity)

    productStyCoeff = getElement('stoichiometricCoefficient', BP)
    addAttr(productStyCoeff, BP, 'datatype', 'xsd:float')
    productStyValue = rxnDesc['products'][productID]['stoichiometry']
    if productStyValue is None:
        productStyCoeff.text = '1.0'
    else:
        productStyCoeff.text = productStyValue

    productSty.append(productStyCoeff)
    owl.append(productSty)