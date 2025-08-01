# Sistema de Autenticação Centralizada

## Visão Geral

O sistema de autenticação centralizada foi implementado para gerenciar automaticamente os cookies de várias plataformas de vídeo (YouTube, Instagram, Facebook, etc.), eliminando a necessidade de os usuários instalarem extensões ou lidarem manualmente com cookies.

## Funcionalidades

- Login automático em várias plataformas
- Atualização diária de cookies
- Armazenamento seguro de cookies em formato compatível com yt-dlp
- Integração transparente com o serviço de download de vídeos

## Componentes

### 1. Serviço de Autenticação (`auth_service.py`)

- Gerencia credenciais para diferentes plataformas
- Realiza login automatizado usando Selenium
- Extrai e salva cookies em formato compatível com yt-dlp
- Fornece cookies atualizados para o serviço de download

### 2. Job de Atualização de Cookies (`cookie_update_job.py`)

- Agenda atualizações diárias de cookies
- Inicializa o processo de login para todas as plataformas configuradas
- Gerencia credenciais para diferentes plataformas

## Plataformas Suportadas

- YouTube (Google)
- Instagram
- Facebook
- Kwai
- Pinterest

## Configuração

### Dependências

O sistema requer as seguintes dependências adicionais:

```
selenium==4.15.2
webdriver-manager==4.0.2
schedule==1.2.1
```

### Navegadores

O sistema suporta os seguintes navegadores:

- Chrome (principal): Utilizado como primeira opção para automação
- Firefox (fallback): Utilizado automaticamente se o Chrome não estiver disponível

### Credenciais

As credenciais são configuradas no arquivo `cookie_update_job.py`. Por padrão, o sistema está configurado com as seguintes credenciais para o YouTube:

```python
self.auth_service.set_credentials(
    "youtube", 
    "cut.py01@gmail.com", 
    "G@bryel123"
)
```

Para adicionar credenciais para outras plataformas, você pode modificar o método `start()` no arquivo `cookie_update_job.py`.

## Funcionamento

1. Quando a aplicação é iniciada, o job de atualização de cookies é iniciado automaticamente
2. O job realiza login em todas as plataformas configuradas e salva os cookies
3. Os cookies são atualizados diariamente às 3:00 da manhã
4. Quando um usuário solicita o download de um vídeo, o serviço de vídeo verifica se existem cookies centralizados para a plataforma correspondente
5. Se existirem, os cookies são utilizados automaticamente para o download

## Segurança

- As credenciais são armazenadas apenas em memória durante a execução da aplicação
- Os cookies são armazenados em arquivos locais no servidor
- O acesso aos cookies é restrito ao serviço de download

## Limitações

- O sistema utiliza Chrome como navegador principal e Firefox como fallback caso o Chrome não esteja disponível.
- Algumas plataformas podem detectar automação e solicitar verificações adicionais
- Alterações nas interfaces de login das plataformas podem exigir atualizações no código
- Algumas plataformas podem ter políticas contra automação de login

## Solução de Problemas

- **Erro de login**: Verifique se as credenciais estão corretas e se o formato do arquivo `.env` está adequado.
- **Falha na automação com Chrome**: 
  - Verifique se o Chrome está instalado no sistema
  - Certifique-se de que a versão do ChromeDriver é compatível com sua versão do Chrome
  - Verifique se o caminho do Chrome está correto nos logs
  - O sistema tentará usar Firefox como fallback automaticamente
- **Falha na automação com Firefox**: 
  - Verifique se o Firefox está instalado no sistema
  - Certifique-se de que a versão do GeckoDriver é compatível com sua versão do Firefox
- **Erro "não é uma aplicação de Win32 válida"**: 
  - Este erro geralmente ocorre quando há incompatibilidade entre a arquitetura do driver e do sistema
  - O sistema agora tenta múltiplas abordagens para resolver isso automaticamente:
    1. Tenta inicializar o ChromeDriver sem especificar arquitetura
    2. Tenta inicializar o Chrome diretamente sem WebDriver Manager
    3. Procura o ChromeDriver em caminhos específicos conhecidos
    4. Realiza uma busca recursiva pelo ChromeDriver no diretório `.wdm`
    5. Se todas as tentativas falharem, tenta usar o Firefox como fallback
- **Cookies não funcionam**: Alguns sites podem exigir autenticação adicional ou podem ter alterado sua estrutura. Verifique os logs para mais detalhes.