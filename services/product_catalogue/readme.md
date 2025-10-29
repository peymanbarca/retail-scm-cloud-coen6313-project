
# Build docker image

    sudo docker build -t grpcacr123.azurecr.io/product-catalogue-service:latest .


# Push docker image to Azure container registry (ACR)

    sudo docker login grpcacr123.azurecr.io
    sudo docker push grpcacr123.azurecr.io/product-catalogue-service:latest


# deploy to Azure container app

    az containerapp create \
      --name product-catalogue-service \
      --resource-group flask-rg1 \
      --environment azcapp-env \
      --image grpcacr123.azurecr.io/product-catalogue-service:latest \
      --target-port 8004 \
      --ingress external \
      --transport http \
      --registry-server grpcacr123.azurecr.io \
      --registry-username x \
      --registry-password y \
      --env-vars MONGO_URI="mongodb+srv://x:y@retail-mongo-db.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"


    az containerapp logs show \
    --name product_catalogue_service \
    --resource-group flask-rg1 \
    --follow

    curl -v -k https://product-catalogue-service.yellowocean-608034e9.canadacentral.azurecontainerapps.io/docs