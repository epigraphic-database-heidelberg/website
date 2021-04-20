from lxml import etree
from flask import current_app
from flask_babel import _
import re


def to_xml(inscription):
    """
    converts inscription data to EpiDoc XML
    """
    xml = bytes(bytearray(epidoc_template, encoding='utf-8'))
    root = etree.fromstring(xml)

    title_element = root.find('*//{http://www.tei-c.org/ns/1.0}titleStmt/{http://www.tei-c.org/ns/1.0}title')
    if title_element is not None:
        title_element.text = inscription.titel
    
    publicationStmt_elem = root.find('*//{http://www.tei-c.org/ns/1.0}publicationStmt')
    if publicationStmt_elem is not None:
        publicationStmt_elem.append(etree.XML("<idno type='localID'>"+inscription.hd_nr+"</idno>"))
        publicationStmt_elem.append(etree.XML("<idno type='URI'>"+current_app.config['HOST']+"/edh/inschrift/"+inscription.hd_nr+"</idno>"))

    repository_elem = root.find('*//{http://www.tei-c.org/ns/1.0}msIdentifier/{http://www.tei-c.org/ns/1.0}repository')
    if repository_elem is not None:
        repository_elem.text = inscription.aufbewahrung

    support_elem = root.find('*//{http://www.tei-c.org/ns/1.0}support')
    if support_elem is not None and inscription.i_traeger_str is not None:
        support_elem.append(etree.XML("<objectType ref='"+_get_eagle_uri_for_objecttype(inscription.i_traeger)+"'>"+inscription.i_traeger_str+"</objectType>"))
    if support_elem is not None and inscription.material is not None:
        support_elem.append(etree.XML("<material ref='#'>"+inscription.material+"</material>"))
    if support_elem is not None and (inscription.hoehe is not None or inscription.breite is not None or inscription.tiefe is not None):
        support_elem.append(etree.XML("<dimensions unit='cm'></dimensions>"))
        dimensions_elem = root.find('*//dimensions')
        if dimensions_elem is not None and (inscription.hoehe is not None):
            dimensions_elem.append(etree.XML("<height>"+inscription.hoehe+"</height>"))
        if dimensions_elem is not None and (inscription.breite is not None):
            dimensions_elem.append(etree.XML("<width>"+inscription.breite+"</width>"))
        if dimensions_elem is not None and (inscription.tiefe is not None):
            dimensions_elem.append(etree.XML("<depth>"+inscription.tiefe+"</depth>"))
    if support_elem is not None and inscription.dekor is not None:
        support_elem.append(etree.XML("<rs type='decoration' ref='http://www.eagle-network.eu/voc/decor/lod/2000'>yes</rs>"))
    else:
        support_elem.append(etree.XML("<rs type='decoration' ref='http://www.eagle-network.eu/voc/decor/lod/1000'>no</rs>"))

    handDesc_elem = root.find('*//{http://www.tei-c.org/ns/1.0}handDesc')
    if handDesc_elem is not None and inscription.bh is not None:
        handDesc_elem.append(etree.XML("<dimensions><height unit='cm'>"+inscription.bh+"</height></dimensions>"))

    origin_elem = root.find('*//{http://www.tei-c.org/ns/1.0}origin')
    if origin_elem is not None and (inscription.provinz is not None or inscription.fo_antik is not None):
        origin_elem.append(etree.XML("<origPlace/>"))
        origPlace_elem = root.find('*//origPlace')
        if inscription.provinz is not None:
            origPlace_elem.append(etree.XML("<placeName type='province'>"+inscription.provinz+"</placeName>"))
        if inscription.fo_antik is not None:
            if inscription.pl_ancient_loc1 is not None:
                origPlace_elem.append(etree.XML("<placeName type='ancient' ref='https://pleiades.stoa.org/places/"+str(inscription.pl_ancient_loc1)+"'>"+inscription.fo_antik+"</placeName>"))
            else:
                origPlace_elem.append(etree.XML("<placeName type='ancient' ref='#'>"+inscription.fo_antik+"</placeName>"))

    if origin_elem is not None and (inscription.dat_jahr_a is not None or inscription.dat_jahr_e is not None):
        origin_elem.append(etree.XML("<origDate/>"))
        origDate_elem = root.find('*//origDate')
        not_before = ""
        not_after = ""
        when = ""
        dat_str = ""
        if inscription.dat_jahr_a and inscription.dat_jahr_e:
            if inscription.dat_jahr_a:
                if inscription.dat_jahr_a < 0:
                    not_before = "notBefore-custom='"+str(inscription.dat_jahr_a).zfill(5)+"'"
                    dat_str += str(inscription.dat_jahr_a).replace("-", "") + " BC - "
                else:
                    not_before = "notBefore-custom='"+str(inscription.dat_jahr_a).zfill(4)+"'"
                    dat_str += str(inscription.dat_jahr_a).replace("-", "") + " AD - "
            if inscription.dat_jahr_e:
                if inscription.dat_jahr_e < 0:
                    not_after = "notAfter-custom='"+str(inscription.dat_jahr_e).zfill(5)+"'"
                    dat_str += str(inscription.dat_jahr_e).replace("-", "") + " BC"
                else:
                    not_after = "notAfter-custom='"+str(inscription.dat_jahr_e).zfill(4)+"'"
                    dat_str += str(inscription.dat_jahr_e).replace("-", "") + " AD"
        else:
            when = "when-custom='"+str(inscription.dat_jahr_a).zfill(4)+"'"
            if inscription.dat_jahr_a < 0:
                dat_str += str(inscription.dat_jahr_a).replace("-", "") + " BC"
            else:
                dat_str += str(inscription.dat_jahr_a).replace("-", "") + " AD"
        origDate_elem.append(etree.XML("<origDate "+not_before+" " + not_after + " " + when + " datingMethod='http://en.wikipedia.org/wiki/Julian_calendar'>" + dat_str + "</origDate>"))

    provenance_elem = root.find('*//{http://www.tei-c.org/ns/1.0}provenance')
    if provenance_elem is not None and (inscription.land is not None or inscription.fo_modern is not None or inscription.fundstelle is not None or inscription.verw_bezirk is not None):
        if inscription.land is not None:
            provenance_elem.append(etree.XML("<placeName type='country'>"+inscription.land+"</placeName>"))
        if inscription.fo_modern is not None:
            geonames_uri = ""
            if inscription.geo_id1 is not None:
                geonames_uri = "ref='http://www.geonames.org/" + str(inscription.geo_id1) + "'"
            provenance_elem.append(etree.XML("<placeName type='modern' "+geonames_uri+">"+inscription.fo_modern+"</placeName>"))
        if inscription.fundstelle is not None:
            provenance_elem.append(etree.XML("<placeName type='findspot'>"+inscription.fundstelle+"</placeName>"))
        if inscription.verw_bezirk is not None:
            provenance_elem.append(etree.XML("<placeName type='region'>"+inscription.verw_bezirk+"</placeName>"))
    if provenance_elem is not None and inscription.fundjahr is not None:
        provenance_elem.attrib['when'] = str(inscription.fundjahr)

    keywords_elem = root.find('*//{http://www.tei-c.org/ns/1.0}keywords')
    if keywords_elem is not None and inscription.i_gattung_str is not None:
        keywords_elem.append(etree.XML("<term ref='#'>"+inscription.i_gattung_str+"</term>"))

    revisionDesc_elem = root.find('*//{http://www.tei-c.org/ns/1.0}revisionDesc')
    if revisionDesc_elem is not None:
        revisionDesc_elem.append(etree.XML("<change when='" + inscription.datum + "' who='"+inscription.bearbeiter+"'>"+_("beleg-"+inscription.beleg)+"</change>"))

    commentary_element = root.find('*//{http://www.tei-c.org/ns/1.0}div[@type="commentary"]/{http://www.tei-c.org/ns/1.0}p')
    if commentary_element is not None:
        commentary_element.text = xmlesc(inscription.kommentar)
    
    biblio_element = root.find('*//{http://www.tei-c.org/ns/1.0}div[@type="bibliography"]/{http://www.tei-c.org/ns/1.0}listBibl')
    if biblio_element is not None:
        bibs = inscription.literatur.split("#")
        for bib in bibs:
            biblio_element.append(etree.XML("<bibl>"+xmlesc(bib.strip())+"</bibl>"))

    edition_elem = root.find('*//{http://www.tei-c.org/ns/1.0}div[@type="edition"]/{http://www.tei-c.org/ns/1.0}ab')
    if edition_elem is not None:
        edition_elem.text = inscription.atext
    
    return etree.tostring(root.getroottree(), pretty_print=True, xml_declaration=True, encoding='UTF-8')


def _get_eagle_uri_for_objecttype(objecttype):
    """
    returns URI of EAGLE objecttype vocabulary
    see: https://www.eagle-network.eu/voc/objtyp.html
    """
    fragezeichen = ""
    if re.search(".+\?$", objecttype):
        objecttype = re.sub("\?$", "", objecttype)
        fragezeichen = "?"
    switcher = {
        "Altar": "https://www.eagle-network.eu/voc/objtyp/lod/29",
        "Architekturteil": "https://www.eagle-network.eu/voc/objtyp/lod/35",
        "Bueste": "https://www.eagle-network.eu/voc/objtyp/lod/135",
        "Bank": "https://www.eagle-network.eu/voc/objtyp/lod/254",
        "Barren": "https://www.eagle-network.eu/voc/objtyp/lod/154",
        "Basis": "https://www.eagle-network.eu/voc/objtyp/lod/53",
        "Block": "https://www.eagle-network.eu/voc/objtyp/lod/189",
        "Brunnen": "https://www.eagle-network.eu/voc/objtyp/lod/40",
        "Cippus": "https://www.eagle-network.eu/voc/objtyp/lod/85",
        "Clipeus": "https://www.eagle-network.eu/voc/objtyp/lod/94",
        "Cupa": "https://www.eagle-network.eu/voc/objtyp/lod/112",
        "Diptychon": "https://www.eagle-network.eu/voc/objtyp/lod/118",
        "EhrenVotivbogen": "https://www.eagle-network.eu/voc/objtyp/lod/20",
        "EhrenVotivsäule": "https://www.eagle-network.eu/voc/objtyp/lod/102",
        "Fels": "https://www.eagle-network.eu/voc/objtyp/lod/210",
        "Grabbau": "https://www.eagle-network.eu/voc/objtyp/lod/230",
        "Herme": "https://www.eagle-network.eu/voc/objtyp/lod/132",
        "instrdom": "https://www.eagle-network.eu/voc/objtyp/lod/140",
        "instrmil": "https://www.eagle-network.eu/voc/objtyp/lod/141",
        "instrsac": "https://www.eagle-network.eu/voc/objtyp/lod/142",
        "Meilenstein": "https://www.eagle-network.eu/voc/objtyp/lod/89",
        "Mensa": "https://www.eagle-network.eu/voc/objtyp/lod/157",
        "Olla": "https://www.eagle-network.eu/voc/objtyp/lod/182",
        "Pflaster": "https://www.eagle-network.eu/voc/objtyp/lod/190",
        "Platte": "https://www.eagle-network.eu/voc/objtyp/lod/260",
        "Relief": "https://www.eagle-network.eu/voc/objtyp/lod/24",
        "Sarkophag": "https://www.eagle-network.eu/voc/objtyp/lod/214",
        "Schmuck": "https://www.eagle-network.eu/voc/objtyp/lod/163",
        "Skulptur": "https://www.eagle-network.eu/voc/objtyp/lod/224",
        "Stadtbefestigung": "https://www.eagle-network.eu/voc/objtyp/lod/67",
        "Statue": "https://www.eagle-network.eu/voc/objtyp/lod/241",
        "Statuenbasis": "https://www.eagle-network.eu/voc/objtyp/lod/57",
        "Stele": "https://www.eagle-network.eu/voc/objtyp/lod/250",
        "Tafel": "https://www.eagle-network.eu/voc/objtyp/lod/257",
        "Tessera": "https://www.eagle-network.eu/voc/objtyp/lod/276",
        "Urne": "https://www.eagle-network.eu/voc/objtyp/lod/78",
        "Waffe": "https://www.eagle-network.eu/voc/objtyp/lod/42",
        "Ziegel": "https://www.eagle-network.eu/voc/objtyp/lod/147",
    }
    return switcher.get(objecttype, "")

def xmlesc(txt):
    """
    escape XML string
    """
    if txt is not None:
        return txt.translate(table)

table = str.maketrans({
    "<": "&lt;",
    ">": "&gt;",
    "&": "&amp;",
    "'": "&apos;",
    '"': "&quot;",
})

epidoc_template = """<?xml version="1.0" encoding="UTF-8"?><?xml-model href="http://www.stoa.org/epidoc/schema/latest/tei-epidoc.rng" schematypens="http://relaxng.org/ns/structure/1.0"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title/>
            </titleStmt>
            <publicationStmt>
                <authority>Epigraphische Datenbank Heidelberg</authority>
                <availability>
                    <p>Heidelberger Akademie der Wissenschaften</p>
                    <licence target="http://creativecommons.org/licenses/by-sa/4.0/">This file is licensed under the Creative Commons Attribution-ShareAlike 4.0 license.
                    </licence>
                </availability>
            </publicationStmt>
            <sourceDesc>
                <msDesc>
                    <msIdentifier>
                        <repository/>
                    </msIdentifier>
                    <physDesc>
                        <objectDesc>
                            <supportDesc>
                                <support/>
                            </supportDesc>
                            <layoutDesc>
                                <layout>description of text field/campus</layout>
                            </layoutDesc>
                        </objectDesc>
                        <handDesc/>
                    </physDesc>
                    <history>
                        <origin/>
                        <provenance type="found"/>
                    </history>
                </msDesc>
            </sourceDesc>
        </fileDesc>
        <encodingDesc>
             <p>Encoded following EpiDoc guidelines 9.2</p>
        </encodingDesc>             
        <profileDesc>
            <langUsage>
                <language ident="en">English</language>
                <language ident="de">Deutsch</language>
                <language ident="lat">Latin</language>
            </langUsage>
            <textClass>
                <keywords/>
            </textClass>
            <particDesc>
                <listPerson/>
            </particDesc>
        </profileDesc>
        <revisionDesc/>
    </teiHeader>
    <facsimile>
        <graphic url="photograph of text or monument"/>
    </facsimile>
    <text>
        <body>
            <div type="edition" xml:space="preserve">
                <ab/>
            </div>
            <div type="commentary">
                <p/>
            </div>
            <div type="bibliography">
                <listBibl/>
            </div>
        </body>
    </text>
</TEI>
"""