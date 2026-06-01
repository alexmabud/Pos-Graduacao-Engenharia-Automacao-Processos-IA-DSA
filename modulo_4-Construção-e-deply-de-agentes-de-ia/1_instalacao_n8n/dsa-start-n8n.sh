#!/bin/bash

# Define nome do volume e da imagem
VOLUME_NAME="n8n_data"
CONTAINER_NAME="n8n"
N8N_VERSION="1.109.1"

# Cria volume se não existir
docker volume inspect $VOLUME_NAME > /dev/null 2>&1 || docker volume create $VOLUME_NAME

# Executa container em modo destacado com a versão fixa
docker run -d \
  --name $CONTAINER_NAME \
  -p 5678:5678 \
  -v $VOLUME_NAME:/home/node/.n8n \
  n8nio/n8n:$N8N_VERSION
