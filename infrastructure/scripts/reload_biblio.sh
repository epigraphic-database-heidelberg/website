#!/bin/sh

curl http://localhost:8983/solr/edhBiblio/update --data '<delete><query>*:*</query></delete>' -H 'Content-type:text/xml; charset=utf-8'

curl http://localhost:8983/solr/edhBiblio/update --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'

solr restart

sleep 5

curl 'http://localhost:8983/solr/edhBiblio/update?commit=true' --data-binary @../data/edh_data_biblio.csv -H 'Content-type:application/csv'

