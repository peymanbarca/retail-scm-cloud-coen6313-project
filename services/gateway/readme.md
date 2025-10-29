
# Build docker image

    sudo docker build -t grpcacr123.azurecr.io/gateway-service:latest .

# Push docker image to Azure container registry (ACR)

    sudo docker login grpcacr123.azurecr.io
    sudo docker push grpcacr123.azurecr.io/gateway-service:latest

# deploy to Azure container app

    az containerapp create \
      --name gateway-service \
      --resource-group flask-rg1 \
      --environment azcapp-env \
      --image grpcacr123.azurecr.io/gateway-service:latest \
      --target-port 8000 \
      --ingress external \
      --transport http \
      --registry-server grpcacr123.azurecr.io \
      --registry-username x \
      --registry-password y \
      --env-vars CATALOGUE_URL="https://product-catalogue-service.yellowocean-608034e9.canadacentral.azurecontainerapps.io" \
                 ORDER_URL="https://order-service.yellowocean-608034e9.canadacentral.azurecontainerapps.io" \
                 PAYMENT_URL="https://payment-service.yellowocean-608034e9.canadacentral.azurecontainerapps.io"


    az containerapp logs show \
    --name gateway-service \
    --resource-group flask-rg1 \
    --follow

    curl -v -k https://gateway-service.yellowocean-608034e9.canadacentral.azurecontainerapps.io/docs