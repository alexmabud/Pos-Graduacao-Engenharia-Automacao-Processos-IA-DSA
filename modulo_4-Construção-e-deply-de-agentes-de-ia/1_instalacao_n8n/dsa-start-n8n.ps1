$ContainerName = "n8n"
$VolumeName = "n8n_data"
$N8NVersion = "1.109.1"

$volumeExists = docker volume inspect $VolumeName > $null 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Criando volume..."
    docker volume create $VolumeName
}

# Remove container antigo, se existir
docker rm -f $ContainerName > $null 2>&1

# Executa o container
docker run -d --name $ContainerName -p 5678:5678 -v ${VolumeName}:/home/node/.n8n n8nio/n8n:$N8NVersion

Write-Host "n8n rodando em http://localhost:5678"
