# TXD Texture Studio

Ferramenta em Python para abrir arquivos **TXD (RenderWare Texture Dictionary)** usados em projetos de GTA San Andreas, SAMP e CRMP, visualizar as texturas e exportá-las para PNG.

> **Estado do projeto:** versão inicial com interface gráfica para inspeção e exportação. O programa não modifica nem recompila arquivos TXD.

## Recursos

- Abrir arquivos `.txd`.
- Listar as texturas encontradas no arquivo.
- Pré-visualizar cada textura.
- Exibir a transparência em fundo quadriculado.
- Mostrar dimensões, quantidade de mipmaps e informação de alpha.
- Navegar entre níveis de mipmap.
- Exportar uma textura selecionada.
- Exportar todas as texturas.
- Exportar somente o mipmap principal ou todos os mipmaps.
- Evitar sobrescrever arquivos quando existem nomes de textura repetidos.
- Gerar `txd_report.json` com o resultado da exportação.
- Tratar erros por textura, permitindo continuar a exportação das demais.

## Requisitos

- Python 3.10 ou superior (recomendado).
- Pillow.
- rwfury.
- Tkinter, normalmente incluído na instalação padrão do Python.

## Instalação

Clone o repositório:

```bash
git clone https://github.com/SEU-USUARIO/txd-texture-studio.git
cd txd-texture-studio
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
python -m pip install rwfury pillow
```

Se o comando `python` não funcionar no Windows, tente `py`.

## Executar

```bash
python txd_studio_gui.py
```

A janela será aberta. Clique em **Abrir TXD**, selecione seu arquivo e escolha uma textura na lista.

## Como exportar

### Exportar uma textura

1. Abra um arquivo TXD.
2. Selecione uma textura na lista à esquerda.
3. Clique em **Exportar selecionada**.
4. Escolha a pasta de destino.

### Exportar todas as texturas

1. Abra um arquivo TXD.
2. Clique em **Exportar todas**.
3. Escolha a pasta de destino.
4. Aguarde a conclusão e consulte o relatório JSON.

### Exportar mipmaps

Marque **Exportar todos os mipmaps** antes de exportar.

- Desmarcado: exporta apenas o nível principal.
- Marcado: exporta todos os níveis encontrados, com nomes como `textura_mip0.png`, `textura_mip1.png` etc.

## Estrutura sugerida do repositório

```text
txd-texture-studio/
├── txd_studio_gui.py
├── README.md
├── requirements.txt
└── .gitignore
```

Exemplo de `requirements.txt`:

```text
rwfury
Pillow
```

## Compatibilidade e observações técnicas

O código usa a API apresentada no exemplo original:

```python
from rwfury import Txd

txd = Txd.from_file("arquivo.txd")
for texture in txd.textures:
    mipmaps, has_alpha = texture.to_rgba()
```

A disponibilidade e o comportamento desses métodos dependem da versão instalada do `rwfury`. Se a biblioteca mudar sua API, será necessário adaptar a camada de leitura.

O programa valida o tamanho dos dados RGBA antes de criar cada PNG. Isso evita salvar uma imagem com dimensões incompatíveis com os bytes recebidos.

### Importante sobre TXD e DFF

- **TXD** guarda texturas.
- **DFF** guarda a geometria/modelo 3D.
- Este projeto exporta texturas TXD para PNG.
- Ele ainda não cria TXD, não edita materiais dentro de DFF e não instala veículos no jogo.

Para adicionar um veículo ao SAMP/CRMP, normalmente também é necessário preparar o modelo DFF, as texturas TXD e configurar a substituição/instalação conforme o cliente ou servidor utilizado.

## Solução de problemas

### `ModuleNotFoundError: No module named 'rwfury'`

Instale a biblioteca no mesmo ambiente Python usado para executar o programa:

```bash
python -m pip install rwfury
```

### `No module named PIL`

Instale Pillow:

```bash
python -m pip install pillow
```

### Tkinter não encontrado

No Windows, use uma instalação oficial do Python que inclua Tcl/Tk. Em algumas distribuições Linux, o Tkinter pode precisar ser instalado pelo gerenciador de pacotes do sistema.

### Uma textura não pode ser visualizada

O arquivo pode conter um formato não suportado pela versão atual da biblioteca, mipmaps incompletos ou dados inválidos. Consulte o terminal para obter detalhes do erro.

## Próximas melhorias planejadas

- Edição de texturas com ferramentas de recorte, redimensionamento e ajustes de cor.
- Substituição de uma textura por PNG.
- Criação/regravação de TXD, após confirmar a API de escrita da biblioteca.
- Comparação entre texturas originais e editadas.
- Pré-visualização de materiais aplicados em modelos DFF.
- Exportação em lote de vários arquivos TXD.

## Licença

Defina uma licença antes de distribuir ou aceitar contribuições. Verifique também os termos de uso das bibliotecas utilizadas.

## Créditos

Projeto comunitário para apoiar a inspeção e preparação de texturas em mods de GTA San Andreas, SAMP e CRMP.
