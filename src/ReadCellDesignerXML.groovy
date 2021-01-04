import org.biopax.paxtools.impl.level3.CellularLocationVocabularyImpl
import org.biopax.paxtools.impl.level3.PublicationXrefImpl
import org.biopax.paxtools.impl.level3.UnificationXrefImpl
import org.biopax.paxtools.impl.level3.XrefImpl
import org.biopax.paxtools.model.level3.CellularLocationVocabulary
import org.biopax.paxtools.model.level3.Xref

import java.io.File

import org.sbml.jsbml.*
import org.biopax.paxtools.io.BioPAXIOHandler
import org.biopax.paxtools.io.SimpleIOHandler
import org.biopax.paxtools.model.BioPAXFactory
import org.biopax.paxtools.model.BioPAXLevel
import org.biopax.paxtools.model.Model
import org.biopax.paxtools.model.level3.ProteinReference
import org.biopax.paxtools.model.level3.UnificationXref

import java.io.ByteArrayOutputStream
import java.io.FileInputStream
import java.io.IOException
import java.io.OutputStream

class ReadCellDesignerXML {

    static main(args) {

        SBMLReader reader = new SBMLReader()
        File file = new File('sim0.xml')
        SBMLDocument sbmlDoc = reader.readSBML(file)

        org.sbml.jsbml.Model CDModel = sbmlDoc.getModel()

        BioPAXFactory bioPAXFactory = BioPAXLevel.L3.getDefaultFactory()
        org.biopax.paxtools.model.Model BPModel = bioPAXFactory.createModel()
        BPModel.setXmlBase("http://www.pantherdb.org/pathways/biopax#")

        for(compartment in CDModel.getListOfCompartments()) {
            BPModel.addNew(CellularLocationVocabulary, compartment.getId())
        }
        output(BPModel, "sim0-converted.owl")
    }

    public static void output(org.biopax.paxtools.model.Model model, String filename) throws IOException {
        BioPAXIOHandler simpleExporter = new SimpleIOHandler()
        OutputStream out = new ByteArrayOutputStream()
        simpleExporter.convertToOWL(model, out)

        try (OutputStream outputStream = new FileOutputStream(filename)) {
            out.writeTo(outputStream);
        }
    }

}
