var map = L.map('mapid', { zoomControl:false }).setView([43.105, 11.49], 4);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
}).addTo(map);
map.touchZoom.disable();
map.doubleClickZoom.disable();
map.scrollWheelZoom.disable();
function getColorBearbeitung(d) {
    return d > 4  ? '#D9D9D9' :
           d > 3  ? '#8C8C8C' :
           d > 2  ? '#D9D9D9' :
           d > 1  ? '#C8656D' :
           d > 0  ? '#1F6B3B' :
                    '#585859';
}

function style(feature) {
    return {
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7,
        fillColor: getColor(feature.properties.numberOfInscriptions)
    };
}
function styleBearbeitung(feature) {
    return {
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7,
        fillColor: getColorBearbeitung(feature.properties.numberOfInscriptions)
    };
}
$.getJSON("./static/data/provinceBearbeitung.edh.geojson", function(data) {
    geoJsonBearbeitung = L.geoJson(data, {
    style: styleBearbeitung
    });
    geoJsonBearbeitung.addTo(map);
});

var legendBearbeitung = L.control({position: 'bottomright'});
legendBearbeitung.onAdd = function (mapBearbeitung) {
    var div = L.DomUtil.create('div', 'info legend');
    var legendBearbeitung = "";
    legendBearbeitung += '<p><a href="./inschrift/suche?provinz=Rae&provinz=PaS&provinz=PaI&provinz=Ach&provinz=Epi&provinz=Mak&provinz=Thr&provinz=MoI&provinz=MoS&provinz=Dac&provinz=Dal&provinz=Nor&provinz=AlP&provinz=AlG&provinz=AlC&provinz=AlM&provinz=Bri" style="text-decoration:none;color:#333" target="_parent"><i style="background:' + getColorBearbeitung(1) + '"></i> EDH vollständig bearbeitet</a>';
    legendBearbeitung += '<p><a href="./inschrift/suche?provinz=GeS&provinz=GeI&provinz=Bel" style="text-decoration:none;color:#333" target="_parent"><i style="background:' + getColorBearbeitung(2) + '"></i> EDH in Arbeit</a>';
    legendBearbeitung += '<p><a href="./inschrift/suche?provinz=Asi&provinz=Cre&provinz=GeS&provinz=Bel&provinz=Nar&provinz=Aqu&provinz=Lug&provinz=GeI&provinz=Ass&provinz=Arm&provinz=LyP&provinz=BiP&provinz=Mes&provinz=Gal&provinz=Cap&provinz=Cil&provinz=Cyr&provinz=Aeg&provinz=MaC&provinz=Num&provinz=Afr&provinz=MaT&provinz=Ara&provinz=Syr&provinz=Iud" style="text-decoration:none;color:#333" target="_parent"><i style="background:' + getColorBearbeitung(0) + '"></i> EDH provisorisch bearbeitet</a>';
    legendBearbeitung += '<p><a href="./inschrift/suche?provinz=Umb&provinz=Pic&provinz=Sam&provinz=LaC&provinz=Etr&provinz=Tra&provinz=Lig&provinz=Aem&provinz=VeH&provinz=BrL&provinz=Sic&provinz=Sar&provinz=Cor&provinz=ApC&provinz=Rom" style="text-decoration:none;color:#333" target="_parent"><i style="background:' + getColorBearbeitung(3) + '"></i> EDR</a>';
    legendBearbeitung += '<p><a href="./inschrift/suche?provinz=Bae&provinz=Lus&provinz=HiC" style="text-decoration:none;color:#333" target="_parent"><i style="background:' + getColorBearbeitung(4) + '"></i> HEpOnl</a>';
    div.innerHTML = legendBearbeitung;
    return div;
};
legendBearbeitung.addTo(map);
