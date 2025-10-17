
# Build docker image

    sudo docker build -t grpcacr123.azurecr.io/payment-service:latest .

# Push docker image to Azure container registry (ACR)

    sudo docker login grpcacr123.azurecr.io
    sudo docker push grpcacr123.azurecr.io/payment-service:latest


# deploy to Azure container app

    az extension add --name containerapp --upgrade

    az containerapp env create   --name azcapp-env   --resource-group flask-rg1   --location canadacentral

    az containerapp create \
    --name payment-service \
    --resource-group flask-rg1 \
    --environment azcapp-env \
    --image grpcacr123.azurecr.io/payment-service:latest \
    --target-port 8003 \
    --ingress external \
    --transport http 
    --registry-server grpcacr123.azurecr.io \
    --registry-username x \
    --registry-password y


    az containerapp logs show \
    --name payment-service \
    --resource-group flask-rg1 \
    --follow

    curl -v -k https://payment-service.yellowocean-608034e9.canadacentral.azurecontainerapps.io/docs