import collections
import re
from datetime import datetime

import pysolr
from babel.dates import format_date
from babel.numbers import format_decimal
from flask import Markup
from flask import current_app
from flask_babel import lazy_gettext as _l

from edh_web_application.models.Place import Place
from edh_web_application.models.helpers import get_fullname


class Inscription:

    historic_periods = (
        _l('per_1'), _l('per_2'), _l('per_3'), _l('per_4'), _l('per_5'), _l('per_6'), _l('per_7'), _l('per_8'), _l('per_9'), _l('per_10'),
        _l('per_11'), _l('per_12'), _l('per_13'), _l('per_14'), _l('per_15'), _l('per_16'), _l('per_17'), _l('per_18'), _l('per_19'), _l('per_20'),
        _l('per_21'), _l('per_22'), _l('per_23'), _l('per_24'), _l('per_25'), _l('per_26')
    )

    type_of_inscription = (
        _l('titaccl'), _l('titadnun'), _l('titadsig'), _l('nota'), _l('titoppubpriv'), _l('titreiexpl'), _l('titpossfabr'), _l('brief'),
        _l('titdefix'), _l('tithon'), _l('elogium'), _l('oratio'), _l('titsep'), _l('titterm'), _l('fasti'), _l('miliarium'), _l('diplmil'), _l('titiurpub'), _l('titiurpriv'),
        _l('titsedspect'), _l('indexlaterc'), _l('titsac')
    )
    type_of_monument = (
        _l('Altar'), _l('Architekturteil'), _l('Barren'), _l('Basis'), _l('Bank'), _l('Block'), _l('Bueste'), _l('Cippus'), _l('Fels'), _l('Cupa'), _l('Diptychon'),
        _l('Stadtbefestigung'),_l('Brunnen'), _l('Grabbau'), _l('Herme'), _l('EhrenVotivbogen'), _l('EhrenVotivsäule'), _l('instrdom'), _l('instrmil'), _l('instrsac'), _l('Schmuck'), _l('Meilenstein'),
        _l('Olla'),_l('Pflaster'), _l('Relief'), _l('Sarkophag'), _l('Skulptur'), _l('Clipeus'), _l('Platte'), _l('Statue'), _l('Statuenbasis'),
        _l('Stele'), _l('Mensa'), _l('Tafel'), _l('Tessera'), _l('Ziegel'), _l('Urne'), _l('Waffe')
    )

    hd_nr_redirects = {
        'HD011276': 'HD057246',
        'HD017892': 'HD057373',
        'HD010828': 'HD023069',
        'HD017885': 'HD037941',
        'HD021357': 'HD014614',
        'HD018707': 'HD014291',
        'HD021127': 'HD016969',
        'HD029079': 'HD014262',
        'HD004223': 'HD025002',
        'HD005872': 'HD002917',
        'HD018408': 'HD004384',
        'HD047178': 'HD045537',
        'HD051803': 'HD001824',
        'HD051802': 'HD001827',
        'HD006393': 'HD007134',
        'HD024430': 'HD024427',
        'HD025458': 'HD023091',
        'HD023254': 'HD023248',
        'HD046812': 'HD011502',
        'HD015496': 'HD010177',
        'HD000526': 'HD037323',
        'HD008154': 'HD059028',
        'HD008145': 'HD008142',
        'HD009263': 'HD011265',
        'HD038836': 'HD038835',
        'HD061087': 'HD054675',
        'HD019880': 'HD021698',
        'HD065003': 'HD066830',
        'HD019565': 'HD006071',
        'HD017447': 'HD059411',
        'HD021898': 'HD059433',
        'HD022030': 'HD019674',
        'HD022054': 'HD059497',
        'HD059078': 'HD021931',
        'HD059089': 'HD021546',
        'HD059246': 'HD059418',
        'HD059247': 'HD059330',
        'HD059366': 'HD022057',
        'HD059371': 'HD059411',
        'HD059431': 'HD045503',
        'HD059434': 'HD059483',
        'HD059442': 'HD059463',
        'HD059450': 'HD059333',
        'HD012572': 'HD012569',
        'HD059480': 'HD059463',
        'HD059505': 'HD059370',
        'HD059816': 'HD017438',
        'HD033027': 'HD059602',
        'HD024286': 'HD042483',
        'HD004902': 'HD006666',
        'HD013413': 'HD017617',
        'HD005554': 'HD022855',
        'HD042497': 'HD054675',
        'HD016860': 'HD009075',
        'HD045584': 'HD035936',
        'HD002799': 'HD002796',
        'HD025555': 'HD024139',
        'HD008251': 'HD008248',
        'HD023251': 'HD023248',
        'HD023257': 'HD023248',
        'HD023260': 'HD023248',
        'HD023263': 'HD023248',
        'HD023266': 'HD023248',
        'HD023269': 'HD023248',
        'HD023272': 'HD035936',
        'HD023275': 'HD035936',
        'HD023278': 'HD035936',
        'HD010132': 'HD015490',
        'HD010093': 'HD015493',
        'HD015502': 'HD010078',
        'HD030747': 'HD028276',
        'HD034267': 'HD040008',
        'HD038281': 'HD050983',
        'HD015694': 'HD031398',
        'HD018801': 'HD023458',
        'HD049759': 'HD049758',
        'HD057627': 'HD019735',
        'HD017964': 'HD035561',
        'HD009817': 'HD036064',
        'HD011658': 'HD018442',
        'HD045442': 'HD004393',
        'HD044892': 'HD011632',
        'HD000485': 'HD067423',
        'HD020367': 'HD005857',
        'HD031120': 'HD019766',
        'HD008437': 'HD007199',
        'HD057868': 'HD034668',
        'HD063568': 'HD064712',
        'HD042657': 'HD007125',
        'HD055942': 'HD035006',
        'HD055946': 'HD035007',
        'HD055945': 'HD035008',
        'HD055944': 'HD035009',
        'HD004693': 'HD000411',
        'HD025153': 'HD013178',
        'HD026677': 'HD020691',
        'HD030969': 'HD053048',
        'HD031161': 'HD053049',
        'HD054623': 'HD024091',
        'HD054625': 'HD024937',
        'HD050107': 'HD061482',
        'HD038387': 'HD008060',
        'HD018845': 'HD028138',
        'HD019142': 'HD028138',
        'HD061908': 'HD057738',
        'HD061442': 'HD058389',
        'HD043013': 'HD042410',
        'HD036067': 'HD002085',
        'HD022586': 'HD001713',
        'HD009602': 'HD001213',
        'HD019806': 'HD001213',
        'HD024316': 'HD037335',
        'HD037291': 'HD032053',
        'HD020139': 'HD039534',
        'HD012010': 'HD011837',
        'HD031462': 'HD000864',
        'HD022643': 'HD021378',
        'HD021828': 'HD024343',
        'HD021831': 'HD024346',
        'HD014318': 'HD040736',
        'HD019168': 'HD028666',
        'HD021384': 'HD028666',
        'HD016109': 'HD015580',
        'HD020676': 'HD027648',
        'HD046108': 'HD002477',
        'HD032921': 'HD007418',
        'HD015284': 'HD033685',
        'HD003243': 'HD000932',
        'HD015693': 'HD014232',
        'HD010320': 'HD010508',
        'HD010317': 'HD010505',
        'HD010329': 'HD010511',
        'HD029595': 'HD020168',
        'HD035595': 'HD069075',
        'HD016371': 'HD003262',
        'HD016374': 'HD003436',
        'HD016377': 'HD008246',
        'HD016380': 'HD008252',
        'HD016383': 'HD003364',
        'HD003610': 'HD001883',
        'HD044477': 'HD048877',
        'HD046300': 'HD000675',
        'HD003282': 'HD003279',
        'HD004570': 'HD000298',
        'HD039687': 'HD006529',
        'HD009529': 'HD037724',
        'HD009682': 'HD009679',
        'HD012291': 'HD011241',
        'HD012318': 'HD050971',
        'HD027201': 'HD036993',
        'HD008263': 'HD067911',
        'HD019966': 'HD021627',
        'HD016398': 'HD008273',
        'HD016407': 'HD008282',
        'HD016404': 'HD008279',
        'HD016395': 'HD008276',
        'HD071521': 'HD035541',
        'HD068282': 'HD022301',
        'HD037866': 'HD007941',
        'HD045996': 'HD071679',
        'HD047861': 'HD071679',
        'HD007947': 'HD068859',
        'HD008789': 'HD012087',
        'HD006852': 'HD032486',
        'HD014421': 'HD010205',
        'HD015699': 'HD014262',
        'HD027670': 'HD026595',
        'HD010581': 'HD013592',
        'HD031350': 'HD050544',
        'HD021267': 'HD030043',
        'HD021264': 'HD030073',
        'HD020932': 'HD029772',
        'HD012993': 'HD007300',
        'HD015069': 'HD009051',
        'HD019480': 'HD018046',
        'HD026796': 'HD013715',
        'HD005877': 'HD000306',
        'HD028957': 'HD066594',
        'HD033459': 'HD066596',
        'HD051433': 'HD048816',
        'HD005622': 'HD018269',
        'HD021103': 'HD030622',
        'HD008561': 'HD002114',
        'HD008576': 'HD005374',
        'HD022441': 'HD022438',
        'HD022444': 'HD022438',
        'HD022447': 'HD022438',
        'HD022450': 'HD022438',
        'HD022453': 'HD022438',
        'HD008740': 'HD026464',
        'HD071738': 'HD072484',
        'HD016268': 'HD016027',
        'HD042272': 'HD016304',
        'HD022665': 'HD009022',
        'HD007930': 'HD003016',
        'HD006783': 'HD014789',
        'HD015700': 'HD003809',
        'HD001115': 'HD025907',
        'HD001535': 'HD003123',
        'HD039055': 'HD051717',
        'HD016085': 'HD000923',
        'HD010912': 'HD010909',
        'HD012333': 'HD012330',
        'HD012124': 'HD012121',
        'HD012127': 'HD012121',
        'HD012106': 'HD012103',
        'HD032424': 'HD018879',
        'HD011327': 'HD018936',
        'HD011333': 'HD011330',
        'HD011336': 'HD011330',
        'HD011339': 'HD011330',
        'HD018912': 'HD018094',
        'HD002901': 'HD006292',
        'HD037461': 'HD017650',
        'HD018363': 'HD053777',
        'HD028522': 'HD007251',
        'HD037329': 'HD024319',
        'HD023946': 'HD022995',
        'HD072021': 'HD022995',
        'HD072864': 'HD047941',
        'HD073343': 'HD004576',
        'HD059363': 'HD059357',
        'HD072694': 'HD067601',
        'HD072698': 'HD059647',
        'HD040450': 'HD028207',
        'HD043248': 'HD020752',
        'HD042999': 'HD043006',
        'HD042979': 'HD016569',
        'HD043496': 'HD016569',
        'HD037333': 'HD000532',
        'HD038115': 'HD037226',
        'HD037384': 'HD020984',
        'HD031570': 'HD071723',
        'HD074163': 'HD073419',
        'HD045109': 'HD038466',
        'HD039622': 'HD020431',
        'HD032140': 'HD045399',
        'HD011548': 'HD048583',
        'HD033680': 'HD006045',
        'HD039562': 'HD039564',
        'HD021165': 'HD013920',
        'HD074381': 'HD047934',
        'HD028632': 'HD021503',
        'HD066932': 'HD072975',
        'HD040264': 'HD009538',
        'HD036041': 'HD036042',
        'HD037727': 'HD050969',
        'HD037728': 'HD050970',
        'HD074726': 'HD068820',
        'HD034855': 'HD074664',
        'HD033836': 'HD035923',
        'HD074791': 'HD040183',
        'HD065744': 'HD065743',
        'HD043280': 'HD032292',
        'HD021905': 'HD000529',
        'HD021335': 'HD021323',
        'HD037441': 'HD052242',
        'HD067763': 'HD040269',
        'HD043186': 'HD001340',
        'HD063786': 'HD063785',
        'HD026251': 'HD022018',
        'HD027171': 'HD067478',
        'HD031665': 'HD060448',
        'HD031881': 'HD060721',
        'HD031884': 'HD060723',
        'HD026316': 'HD043435',
        'HD058086': 'HD058085',
        'HD058087': 'HD058085',
        'HD072611': 'HD058091',
        'HD024217': 'HD024214',
        'HD032493': 'HD054854',
        'HD028624': 'HD055284',
        'HD055865': 'HD037281',
        'HD062700': 'HD045560',
        'HD062701': 'HD045561',
        'HD062702': 'HD045562',
        'HD028393': 'HD056176',
        'HD054624': 'HD024934',
        'HD032706': 'HD056148',
        'HD060181': 'HD060303',
        'HD031878': 'HD016019',
        'HD031668': 'HD060098',
        'HD021758': 'HD003764',
        'HD019613': 'HD005388',
        'HD058963': 'HD033115',
        'HD037072': 'HD053791',
        'HD053765': 'HD037071',
        'HD032004': 'HD054545',
        'HD053524': 'HD016303',
        'HD036740': 'HD036736',
        'HD006424': 'HD025056',
        'HD047827': 'HD047826',
        'HD061025': 'HD058072',
        'HD014925': 'HD054375',
        'HD008886': 'HD000467',
        'HD036875': 'HD025146',
        'HD060406': 'HD058069',
        'HD037077': 'HD036737',
        'HD057145': 'HD058286',
        'HD021504': 'HD021501',
        'HD021507': 'HD021501',
        'HD021510': 'HD021501',
        'HD066853': 'HD021611',
        'HD014887': 'HD014809',
        'HD022346': 'HD054855',
        'HD027966': 'HD004906',
        'HD022511': 'HD055486',
        'HD028231': 'HD055778',
        'HD017615': 'HD021930',
        'HD032703': 'HD056286',
        'HD058581': 'HD060210',
        'HD022192': 'HD015363',
        'HD025728': 'HD006308',
        'HD049366': 'HD051304',
        'HD049369': 'HD051307',
        'HD049367': 'HD051305',
        'HD011149': 'HD003308',
        'HD033426': 'HD045657',
        'HD044420': 'HD041134',
        'HD014297': 'HD000513',
        'HD065993': 'HD000546',
        'HD001797': 'HD040424',
        'HD010714': 'HD006314',
        'HD006342': 'HD002468',
        'HD022245': 'HD010862',
        'HD016877': 'HD006518',
        'HD010735': 'HD047741',
        'HD010717': 'HD011102',
        'HD012488': 'HD015651',
        'HD017176': 'HD013771',
        'HD018867': 'HD016168',
        'HD017751': 'HD068131',
        'HD017833': 'HD066245',
        'HD052214': 'HD039576',
        'HD028170': 'HD054622',
        'HD007836': 'HD040406',
        'HD036863': 'HD036864',
        'HD075376': 'HD029166',
        'HD078261': 'HD029172',
        'HD076123': 'HD075650',
        'HD078262': 'HD020360',
        'HD031152': 'HD019941',
        'HD076536': 'HD032526',
        'HD076117': 'HD079138',
        'HD079175': 'HD023513',
        'HD075155': 'HD079162',
        'HD061783': 'HD065345',
        'HD079120': 'HD027738',
        'HD076220': 'HD079008',
        'HD067632': 'HD068195',
        'HD076115': 'HD079001',
        'HD077142': 'HD079094',
        'HD032241': 'HD031035',
        'HD041589': 'HD000326',
        'HD003038': 'HD044369',
        'HD019956': 'HD020155',
        'HD022382': 'HD026605',
        'HD023065': 'HD021186',
        'HD023432': 'HD062689',
        'HD028315': 'HD061796',
        'HD032547': 'HD061796',
        'HD031038': 'HD032244',
        'HD049048': 'HD040788',
        'HD062464': 'HD032031',
        'HD032541': 'HD062463',
        'HD041269': 'HD042200',
        'HD041310': 'HD041137',
        'HD041615': 'HD044408',
        'HD067509': 'HD067428',
        'HD062578': 'HD062688',
        'HD062118': 'HD040765',
        'HD050732': 'HD002399',
        'HD003044': 'HD041689',
        'HD048364': 'HD006115',
        'HD006572': 'HD012251',
        'HD010874': 'HD050061',
        'HD011284': 'HD041111',
        'HD012077': 'HD012143',
        'HD014386': 'HD050069',
        'HD015360': 'HD051259',
        'HD018085': 'HD019605',
        'HD020261': 'HD018103',
        'HD029364': 'HD026829',
        'HD050699': 'HD027515',
        'HD050779': 'HD037529',
        'HD050780': 'HD037533',
        'HD041307': 'HD044422',
        'HD041499': 'HD043868',
        'HD041617': 'HD044409',
        'HD079021': 'HD047818',
        'HD042033': 'HD000103',
        'HD043842': 'HD001858',
        'HD053137': 'HD002350',
        'HD009993': 'HD005080',
        'HD005083': 'HD051424',
        'HD052748': 'HD007139',
        'HD025963': 'HD041137',
        'HD034001': 'HD056306',
        'HD054629': 'HD033993',
        'HD010068': 'HD007472',
        'HD036819': 'HD036750',
        'HD036828': 'HD036829',
        'HD008161': 'HD020344',
        'HD047078': 'HD067577',
        'HD080014': 'HD050317',
        'HD060717': 'HD031524',
        'HD072691': 'HD062223',
        'HD018527': 'HD024418',
        'HD062342': 'HD062199',
        'HD062343': 'HD062199',
        'HD080459': 'HD076017',
        'HD073404': 'HD004861',
        'HD060358': 'HD041633',
        'HD013915': 'HD013912',
        'HD029697': 'HD021975',
        'HD011880': 'HD011887',
        'HD012348': 'HD038311',
        'HD023591': 'HD036574',
        'HD026905': 'HD035282',
        'HD060964': 'HD080490',
        'HD076705': 'HD037074',
        'HD062684': 'HD081057',
        'HD009736': 'HD009733',
        'HD009739': 'HD009733',
        'HD062683': 'HD081300',
        'HD081187': 'HD080696',
        'HD011167': 'HD003284',
        'HD057233': 'HD057227',
        'HD043379': 'HD036227',
        'HD047822': 'HD047821',
        'HD081102': 'HD018120',
        'HD082166': 'HD075573',
        'HD082167': 'HD075575',
        'HD076155': 'HD079211',
        'HD067472': 'HD047805',
        'HD003189': 'HD003183',
        'HD020019': 'HD023014',
        'HD021765': 'HD023014',
        'HD015359': 'HD002011',
        'HD021968': 'HD021965',
        'HD021971': 'HD021965',
        'HD021974': 'HD021965',
        'HD057496': 'HD064332',
        'HD061812': 'HD028312',
        'HD064004': 'HD063084',
        'HD047739': 'HD054569',
        'HD033788': 'HD072310',
        'HD010768': 'HD010765',
        'HD077419': 'HD079937',
        'HD022080': 'HD022077',
        'HD022086': 'HD022083',
        'HD022089': 'HD022083',
        'HD022092': 'HD022083',
        'HD022095': 'HD022083',
        'HD022098': 'HD022083',
        'HD022101': 'HD022083',
        'HD018222': 'HD018219',
        'HD080013': 'HD028791',
    }

    def __init__(self,
                 hd_nr,
                 datum,
                 beleg,
                 **kwargs):
        prop_defaults = {
            "provinz": None,
            "land": None,
            "fo_modern": None,
            "fo_antik": None,
            "fundstelle": None,
            "verw_bezirk": None,
            "fundjahr": None,
            "aufbewahrung": None,
            "i_gattung": None,
            "i_gattung_str": None,
            "i_traeger": None,
            "i_traeger_str": None,
            "material": None,
            "hoehe": None,
            "breite": None,
            "tiefe": None,
            "if_h": None,
            "if_b": None,
            "bh": None,
            "tm_nr": None,
            "gdb_id": None,
            "nl_text": None,
            "metrik": None,
            "dekor": None,
            "schreibtechnik": None,
            "interpunktion": None,
            "dat_jahr_a": None,
            "dat_jahr_e": None,
            "dat_monat": None,
            "dat_tag": None,
            "religion": None,
            "militaer": None,
            "geographie": None,
            "sowire": None,
            "literatur": None,
            "kommentar": None,
            "atext": None,
            "atext_br": None,
            "btext": None,
            "btext_br": None,
            "titel": None,
            "bearbeiter": None,
            "koordinaten1": None,
            "datierung": None,
            "foto_nr": None,
            "provinz_id": None,
        }
        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))
        self.hd_nr = hd_nr
        self.datum = datum
        self.beleg = beleg

    @classmethod
    def query(cls, query_string):
        """
        queries Solr core
        :return: list of Inscription instances
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhText')
        results = solr.search(query_string, **{'rows': '20'})
        if len(results) == 0:
            return None
        else:
            query_result = []
            for result in results:
                props = {}
                for key in result:
                    if key not in ('hd_nr', 'provinz', 'land', 'datum', 'beleg', 'foto_nr', 'atext'):
                        props[key] = result[key]
                    if key == 'land':
                        if re.search(".+\?$", result[key]):
                            key_without_trailing_questionmark = re.sub("\?$", "", result[key])
                            props[key] = Place.country[key_without_trailing_questionmark] + "?"
                        else:
                            props[key] = Place.country[result[key]]
                    elif key == 'provinz':
                        if re.search("\?$", result[key]):
                            key_without_trailing_questionmark = re.sub("\?$", "", result[key])
                            props[key] = _l(key_without_trailing_questionmark) + "?"
                            props['provinz_id'] = Place.get_province_id_from_code(key_without_trailing_questionmark)
                        else:
                            props[key] = _l(result[key])
                            props['provinz_id'] = Place.get_province_id_from_code(result[key])
                        props['provinz_id'] = Place.get_province_id_from_code(re.sub("\?$", "", result[key]))
                    elif key == 'i_gattung':
                        if re.search(".+\?$", result[key]):
                            key_without_trailing_questionmark = re.sub("\?$", "", result[key])
                            props['i_gattung_str'] = _l(key_without_trailing_questionmark) + "?"
                        else:
                            props['i_gattung_str'] = str(_l(result[key]))
                    elif key == 'denkmaltyp':
                        if re.search(".+\?$", result[key]):
                            key_without_trailing_questionmark = re.sub("\?$", "", result[key])
                            props['i_traeger_str'] = _l(key_without_trailing_questionmark) + "?"
                        else:
                            props['i_traeger_str'] = str(_l(result[key]))
                    elif key == 'bearbeiter':
                        props['bearbeiter'] = get_fullname(result['bearbeiter'].lower().capitalize())
                    elif key == 'hoehe':
                        if result[key] < 0:
                            hoehe_str = str(int(result[key])).replace("-", "")
                            props['hoehe'] = "("+hoehe_str+")"
                        else:
                            props['hoehe'] = str(int(result[key]))
                    elif key == 'breite':
                        if result[key] < 0:
                            breite_str = str(int(result[key])).replace("-", "")
                            props['breite'] = "(" + breite_str + ")"
                        else:
                            props['breite'] = str(int(result[key]))
                    elif key == 'tiefe':
                        if result[key] < 0:
                            tiefe_str = str(int(result[key])).replace("-", "")
                            props['tiefe'] = "(" + tiefe_str + ")"
                        else:
                            props['tiefe'] = str(int(result[key]))
                    elif key == 'foto_nr':
                        fotos = result['foto_nr'].split()
                        fotos_list = []
                        for foto in fotos:
                            fotos_list.append(re.sub("[JN]", "", foto))
                        props['foto_nr'] = fotos_list
                    elif key == 'atext':
                        props['atext'] = _prepare_atext(result[key])
                if 'fo_antik' not in props:
                    props['fo_antik'] = ""
                if 'fo_modern' not in props:
                    props['fo_modern'] = ""
                if 'provinz' not in props:
                    props['provinz'] = ""
                if 'i_gattung' not in props:
                    props['i_gattung'] = ""
                if 'dat_jahr_a' not in props:
                    props['dat_jahr_a'] = ""
                if 'dat_jahr_e' not in props:
                    props['dat_jahr_e'] = ""
                if 'dat_monat' not in props:
                    props['dat_monat'] = ""
                if 'dat_tag' not in props:
                    props['dat_tag'] = ""
                props['titel'] = _get_title(props['i_gattung'], props['fo_antik'], props['fo_modern'], props['provinz'])
                if 'fundstelle' in props:
                    fundstelle = re.sub("\{", "<a href='./edh/geographie/"+str(props['gdb_id'])+"'><i class='fas fa-external-link-alt'></i> ", props['fundstelle'])
                    props['fundstelle'] = re.sub("\}","</a>",fundstelle)
                props['datierung'] = _get_date_string(props['dat_jahr_a'], props['dat_jahr_e'], props['dat_monat'], props['dat_tag'])
                atext_br = result['atext']
                props['atext_br'] = Markup(re.sub("/","<br />", atext_br))
                btext_br = result['btext']
                props['btext_br'] = Markup(re.sub("/", "<br />", btext_br))

                inscr = Inscription(result['hd_nr'],
                                    result['datum'],
                                    result['beleg'],
                                    **props
                                    )
                query_result.append(inscr)
            return query_result

    @classmethod
    def get_number_of_records(cls):
        """
        returns number of inscription records from Solr Core edhText
        :return: number of inscription records (str)
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhText')
        results = solr.search("*:*", fq=["-beleg:77", "-beleg:99"])
        return format_decimal(results.hits, locale='de_DE')

    @classmethod
    def get_date_of_last_update(cls):
        """
        returns date of latest update to Solr Core edhText
        :return: date of latest update
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhText')
        results = solr.search("*:*", sort="datum desc", rows=1)
        for res in results:
            dt = datetime.strptime(res['datum'], '%Y-%m-%d').date()
            return format_date(dt, 'd. MMM YYYY', locale='de_DE')

    @classmethod
    def last_updates(cls):
        """
        return last 50 entries that have been updated
        :return: list of 50 entries
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhText')
        results = solr.search("*:*", sort="datum desc", rows=50)
        for res in results:
            if 'dat_jahr_a' not in res:
                res['dat_jahr_a'] = ""
            if 'dat_jahr_e' not in res:
                res['dat_jahr_e'] = ""
            if 'dat_monat' not in res:
                res['dat_monat'] = ""
            if 'dat_tag' not in res:
                res['dat_tag'] = ""
            res['datierung'] = _get_date_string(res['dat_jahr_a'], res['dat_jahr_e'], res['dat_monat'],
                                                  res['dat_tag'])
            dt = datetime.strptime(res['datum'], '%Y-%m-%d').date()
            res['datum'] = format_date(dt, 'd. MMM YYYY', locale='de_DE')
            fragezeichen = ""
            land = res['land']
            if res['land'][-1] == "?":
                fragezeichen = "?"
                land = re.sub("\\?", "", res['land'])
            res['land'] = Place.country[land] + fragezeichen
            fragezeichen = ""
            provinz = res['provinz']
            if res['provinz'][-1] == "?":
                fragezeichen = "?"
                provinz = re.sub("\\?", "", res['provinz'])
            res['provinz'] = Place.province_dict[provinz] + fragezeichen
            res['provinz_id'] = Place.get_province_id_from_code(res['provinz'])
            if 'fundstelle' in res:
                res['fundstelle'] = re.sub("[\{\}]", "", res['fundstelle'])
        return results

    @classmethod
    def group_results_by_date(cls, results):
        """
        groups last 50 entries in geographic database by date
        :param results: list of geographic entries
        :return: orderedDict with date as keys, and list of entries as values
        """
        last_date = ""
        grouped_result = collections.OrderedDict()
        for res in results:
            current_date = res['datum']
            if current_date != last_date:
                grouped_result[current_date] = []
                last_date = current_date
            grouped_result[current_date].append(res)
        return grouped_result


def _get_date_string(dat_jahr_a, dat_jahr_e, monat, tag):
    """
    return description of date of inscription
    :return: date string
    """
    date_str = ""
    if tag != "":
        date_str += str(tag) + ". "
    if monat != "":
        date_str += str(monat) + ". "
    elif monat == "" and tag != "":
        date_str +=  "?. "
    if dat_jahr_a != "":
        if dat_jahr_a < 0:
            if dat_jahr_e != "":
                date_str += str(dat_jahr_a).replace("-", "") + " " + _l("BC") + " &ndash; "
            else:
                date_str += str(dat_jahr_a).replace("-", "") + " " + _l("BC")
        else:
            if dat_jahr_e != "":
                date_str += str(dat_jahr_a) + " " + _l("AD") + " &ndash; "
            else:
                date_str += str(dat_jahr_a) + " " + _l("AD")
    if dat_jahr_e != "":
        if dat_jahr_e < 0:
            date_str += str(dat_jahr_e).replace("-", "") + " " + _l("BC")
        else:
            date_str += str(dat_jahr_e) + " " + _l("AD")
    return date_str


def _get_title(i_gattung="", fo_antik="", fo_modern="", provinz=""):
    """
    returns title for detail view of inscription
    :return: title string
    """
    title_str = ""
    if i_gattung and i_gattung != "":
        i_gatt = i_gattung
        if re.search("\?$", i_gatt):
            key_without_trailing_questionmark = re.sub("\?$", "", i_gatt)
            title_str = _l(key_without_trailing_questionmark) + "?"
        else:
            title_str = _l(i_gatt)
    else:
        title_str = _l("Inschrift")
    if fo_antik and fo_antik != "":
        title_str += _l(" from ") + fo_antik
    elif fo_modern:
        title_str += _l(" from ") + fo_modern
    else:
        provinz = provinz
        if re.search("\?$", provinz):
            key_without_trailing_questionmark = re.sub("\?$", "", provinz)
            title_str += _l(" from ") + _l(key_without_trailing_questionmark) + "?"
        else:
            title_str += _l(" from ") + _l(provinz)
    # uppercase first character
    return title_str[0].upper() + title_str[1:]


def _prepare_atext(atext):
    """
    prepare transcription for display by i.a.:
        break up <f=S>ilius#<f>ilius#SILIUS
    :return: transcription string
    """
    transcription = atext.strip()
    # break up <f=S>ilius#<f>ilius#SILIUS
    if "#" in transcription:
        transcription = ""
        tokenized_atext = atext.split()
        for token in tokenized_atext:
            if "#" in token:
                sub_token = token.split("#")
                transcription += sub_token[0] + " "
            else:
                transcription += token + " "
    # change $ against ------
    transcription = re.sub("\$", "------", transcription)
    # change & against ------
    transcription = re.sub("&", "------", transcription)
    return transcription
