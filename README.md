# Documentação do Projeto - The Video Project

## 1. Visão Geral

### Descrição
The Video Project é uma aplicação web que permite que usuários autenticados enviem vídeos para processamento e façam o download do arquivo final compactado. O projeto foi desenvolvido com um design escalável para lidar com picos de tráfego e garantir alta disponibilidade.

### Objetivos
- Permitir o upload de vídeos por usuários autenticados.
- Processar os vídeos de maneira assíncrona e eficiente.
- Fornecer um sistema de notificação em caso de erro.
- Garantir escalabilidade e resiliência da aplicação.

## 2. Arquitetura

A aplicação segue uma arquitetura baseada em microsserviços e utiliza os seguintes componentes:

- **Backend (Flask)**: API REST responsável por gerenciar os vídeos e autenticação dos usuários.
- **Banco de Dados (PostgreSQL)**: Armazena informações sobre usuários e vídeos processados.
- **Fila de Mensagens (Redis + Celery)**: Gerencia o processamento assíncrono dos vídeos.
- **Orquestração (Kubernetes)**: Gerencia a escalabilidade e alta disponibilidade.
- **Infraestrutura (Terraform)**: Provisiona os recursos necessários na nuvem.

## 3. Tecnologias Utilizadas

- Flask: Framework web em Python.
- PostgreSQL: Banco de dados relacional para persistência dos dados.
- Celery: Para processamento assíncrono de tarefas.
- Redis: Usado como broker de mensagens para o Celery.
- Docker: Containerização dos serviços.
- Kubernetes: Orquestração dos containers, garantindo escalabilidade.
- Terraform: Gerenciamento da infraestrutura na nuvem.
- GitHub: Para CI/CD.

## 4. Implantação com Docker

### 5.1 Construir e Rodar os Containers
docker-compose up --build

### 5.2 Verificar os Containers
docker ps

## 6. Implantação no Kubernetes
A pasta `k8s/` contém os manifests do Kubernetes. Para iniciar a implantação


## 7. Testes e Qualidade
pytest app/tests/test_app.py --disable-warnings -v

coverage run --source=app --omit=app/tests/* -m pytest --disable-warnings
coverage report -m

## 8. CI/CD

A automação do projeto está configurada no GitHub para execução de testes e deploy contínuo. Basta atualizar a branch e abrir uma PR para a MAIN

## 9. Build de imagem

# Build da imagem do app
docker build -t deboraferrarids2/app:latest .
docker push deboraferrarids2/app:latest

# Build da imagem do worker (Celery)
docker build -t deboraferrarids2/worker:latest .
docker push deboraferrarids2/worker:latest

## 10. Segurança

- **Autenticação JWT** para controle de acesso.
- **Banco de Dados Seguro** com variáveis de ambiente para credenciais.
- **Proteção contra SQL Injection e XSS** através de validações de entrada.


------------------------------------

# REQUISITOS ENTREGA

Requisitos esperados para este projeto:

# A nova versão do sistema deve processar mais de um vídeo ao mesmo tempo: 
O uso do Celery permite o processamento assíncrono, permitindo que múltiplos vídeos sejam processados simultaneamente. O HPA (Horizontal Pod Autoscaler) permite escalar a aplicação automaticamente em momentos de pico.

# Em caso de picos o sistema não deve perder uma requisição: 
O Redis está sendo usado como broker para o Celery, permitindo o armazenamento temporário de tarefas.
O Kubernetes HPA assegura que mais pods do aplicativo sejam criados para suportar a carga.

# O Sistema deve ser protegido por usuário e senha:
A autenticação foi implementada de maneira flexivel. Foram criadas tabelas no banco de dados e um fluxo de autenticação considerando cadastro pelo prório projeto, porém a validação passa por uma função que pode ser configurada para validar N possiveis meios de auth no futuro

# O fluxo deve ter uma listagem de status dos vídeos de um usuário:
Usuário pode listar os videos e identificar o status resultado 

# Em caso de erro um usuário pode ser notificado (email ou um outro meio de comunicação)
Via resposta task celery pode ser implementado disparo 

Requisitos técnicos:

# O sistema deve persistir os dados:
O projeto utiliza um banco PostgreSQL para armazenar informações.

# O sistema deve estar em uma arquitetura que o permita ser escalado:
O uso do Kubernetes e do HPA permite escalabilidade automática.

# O projeto deve ser versionado no Github:
O projeto já está versionado.

# O projeto deve ter testes que garantam a sua qualidade:
Utilizando pyteste e coverage inclusive rodando em pipeline

# CI/CD da aplicacao: 
O Terraform é usado para provisionamento de infraestrutura.
O projeto pode ser integrado a pipelines de CI/CD.

