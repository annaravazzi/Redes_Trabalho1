# Aplicação simples de comunicação UDP

Aplicação simples de requisição/download de arquivos em Python usando sockets UDP, com o objetivo de implementar alguns serviços de integridade e segurança na camada de aplicação.

## Protocolo
### Requisição (cliente):
Cliente faz a requisição de um arquivo <filename>. Se ao fim do envio dos pacotes o arquivo não estiver completo, o TIMEOUT é atingido e o cliente faz requisição dos pacotes faltantes.
- Get file: GET_FILE <filename>
- Get packet: GET_PACK <filename> <packet_index>

### Resposta (servidor):
Servidor recebe as requisições do cliente e envia todos os pacotes do arquivo. Se mais pacotes forem requeridos, servidor envia os pacotes separadamente.
- Pacote enviado: OK -> 0 <num_packets> <packet_index> <data_chunk>
- Requisição malformada (checksum incorreto, erro de sintaxe, etc.): BAD_REQUEST -> 1
- Arquivo não encontrado: NOT_FOUND -> 2
- Arquivo muito grande: TOO_LARGE -> 3