# Importação de módulos necessários
from pathlib import Path  # Manipulação de caminhos
import boto3  # Biblioteca AWS SDK para interações com serviços da AWS
from mypy_boto3_rekognition.type_defs import (
    CelebrityTypeDef,
    RecognizeCelebritiesResponseTypeDef,
)  # Tipos de dados específicos do serviço Rekognition
from PIL import Image, ImageDraw, ImageFont  # Manipulação e desenho em imagens

# Inicialização do cliente AWS Rekognition
rekognition_client = boto3.client("rekognition")


def get_image_path(file_name: str) -> str:
    """
    Retorna o caminho absoluto de um arquivo na pasta 'images', 
    relativa ao arquivo atual.
    """
    return str(Path(__file__).parent / "images" / file_name)


def recognize_celebrities(photo_path: str) -> RecognizeCelebritiesResponseTypeDef:
    """
    Envia uma imagem ao serviço AWS Rekognition para reconhecimento de celebridades.

    Args:
        photo_path (str): Caminho do arquivo da imagem.

    Returns:
        RecognizeCelebritiesResponseTypeDef: Resposta do serviço com os detalhes das celebridades reconhecidas.
    """
    with open(photo_path, "rb") as image_file:
        # Envia a imagem em formato binário para o serviço Rekognition
        return rekognition_client.recognize_celebrities(Image={"Bytes": image_file.read()})


def draw_face_boxes(
    image_path: str, output_path: str, faces: list[CelebrityTypeDef]
) -> None:
    """
    Desenha retângulos ao redor das faces reconhecidas e salva o resultado em um novo arquivo.

    Args:
        image_path (str): Caminho da imagem original.
        output_path (str): Caminho para salvar a imagem processada.
        faces (list[CelebrityTypeDef]): Detalhes das faces reconhecidas.
    """
    # Carrega a imagem
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)  # Ferramenta para desenhar sobre a imagem
    font = ImageFont.truetype("Ubuntu-R.ttf", 20)  # Define a fonte para textos

    width, height = image.size  # Dimensões da imagem

    for face in faces:
        box = face["Face"]["BoundingBox"]  # Coordenadas do retângulo da face
        # Converte coordenadas normalizadas para pixels
        left = int(box["Left"] * width)
        top = int(box["Top"] * height)
        right = int((box["Left"] + box["Width"]) * width)
        bottom = int((box["Top"] + box["Height"]) * height)

        confidence = face.get("MatchConfidence", 0)
        if confidence > 90:  # Apenas processa faces com confiança > 90%
            draw.rectangle([left, top, right, bottom], outline="red", width=3)
            name = face.get("Name", "Desconhecido")  # Nome da celebridade
            text_position = (left, top - 20)
            bbox = draw.textbbox(text_position, name, font=font)
            draw.rectangle(bbox, fill="red")
            draw.text(text_position, name, font=font, fill="white")

    # Salva a imagem processada
    image.save(output_path)
    print(f"Imagem processada e salva em: {output_path}")


if __name__ == "__main__":
    # Lista de imagens para processamento
    image_files = ["capr.jpeg", "riana.jpeg", "will.jpg","ss.jpg", "pipoquinha.jpg", "Bonne.jpg", "ior.jpg", "jojo.jpg", "Davi.jpg", "sub.jpg"]
    for image_file in image_files:
        try:
            photo_path = get_image_path(image_file)
            response = recognize_celebrities(photo_path)
            celebrity_faces = response.get("CelebrityFaces", [])

            if not celebrity_faces:
                print(f"Nenhuma celebridade detectada em: {photo_path}")
                continue

            # Gera o caminho para salvar a imagem processada
            output_path = get_image_path(f"{Path(photo_path).stem}-resultado.jpg")
            draw_face_boxes(photo_path, output_path, celebrity_faces)

        except Exception as e:
            print(f"Erro ao processar a imagem {image_file}: {e}")
