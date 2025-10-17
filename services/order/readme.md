
# Build docker image

    sudo docker build -t grpcacr123.azurecr.io/order-service:latest .

# Push docker image to Azure container registry (ACR)

    sudo docker login grpcacr123.azurecr.io
    sudo docker push grpcacr123.azurecr.io/order-service:latest

# deploy to Azure container app

    az containerapp create \
      --name order-service \
      --resource-group flask-rg1 \
      --environment azcapp-env \
      --image grpcacr123.azurecr.io/order-service:latest \
      --target-port 8001 \
      --ingress external \
      --transport http \
      --registry-server grpcacr123.azurecr.io \
      --registry-username x \
      --registry-password y \
      --env-vars MONGO_URI="mongodb+srv://x:y@retail-mongo-db.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000" \
                 INVENTORY_SERVICE_URL="https://inventory-service.internal.yellowocean-608034e9.canadacentral.azurecontainerapps.io" \
                 PAYMENT_SERVICE_URL="https://payment-service.yellowocean-608034e9.canadacentral.azurecontainerapps.io"


    az containerapp logs show \
    --name order-service \
    --resource-group flask-rg1 \
    --follow

    curl -v -k https://order-service.yellowocean-608034e9.canadacentral.azurecontainerapps.io/docs