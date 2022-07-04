curl https://fastdl.mongodb.org/tools/db/mongodb-database-tools-ubuntu1804-x86_64-100.5.3.deb;


mongoimport --db paper2repo \
            --collection papers \
            --drop \
            --jsonArray \
            --batchSize 1 \
            --file ./data/raw/papers-with-abstracts.json \
            --username "root" \
            --password "example" \
            --authenticationDatabase admin \
            --host=0.0.0.0:27017;

