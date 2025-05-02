
#!/bin/bash

if [ ! -d "/app/dist" ] 
then
    npm run build

    echo "Build finished...";

    echo "Delete node_modules folder";

    rm -rf node_modules

    echo "START COPY";

    cp -rf  /app/dist/. /usr/share/nginx/html/

    echo "END COPY";
fi
