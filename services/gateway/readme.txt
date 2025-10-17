
# Build docker image

sudo docker build -t grpcacr123.azurecr.io/gateway-service:latest .

# Push docker image to Azure container registry (ACR)

sudo docker login grpcacr123.azurecr.io
sudo docker push grpcacr123.azurecr.io/gateway-service:latest