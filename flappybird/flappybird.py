import pygame
import os
import random

pygame.init()

tela_largura = 500
tela_altura = 800

img_cano = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
img_background = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
img_chao = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
img_bird = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

pygame.font.init()
font_pts = pygame.font.SysFont('arial', 30)

class Passaro:
    IMGS = img_bird
    Rot_Max = 25
    Vel_Rot = 20
    Tmp_Ani = 5

    def __init__(self, x, y):
        self.y = y
        self.x = x
        self.angulo = 0
        self.vel = 0
        self.altura = self.y
        self.tempo = 0
        self.cont_img = 0
        self.imagens = self.IMGS[0]

    def pular(self):
        self.vel = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo ** 2) + self.vel * self.tempo

        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.Rot_Max:
                self.angulo = self.Rot_Max
        else:
            if self.angulo > -90:
                self.angulo -= self.Vel_Rot

    def desenhar(self, tela):
        self.cont_img += 1
        if self.cont_img < self.Tmp_Ani:
            self.imagens = self.IMGS[0]
        elif self.cont_img < self.Tmp_Ani * 2:
            self.imagens = self.IMGS[1]
        elif self.cont_img < self.Tmp_Ani * 3:
            self.imagens = self.IMGS[2]
        elif self.cont_img < self.Tmp_Ani * 4:
            self.imagens = self.IMGS[1]
        else:
            self.imagens = self.IMGS[0]
            self.cont_img = 0

        if self.angulo <= -80:
            self.imagens = self.IMGS[1]
            self.cont_img = self.Tmp_Ani * 2

        img_rotacionada = pygame.transform.rotate(self.imagens, self.angulo)
        cntr_img = self.imagens.get_rect(topleft=(self.x, self.y)).center
        retangulo = img_rotacionada.get_rect(center=(cntr_img))
        tela.blit(img_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagens)


class Cano:
    distancia = 200
    velocidade = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_top = 0
        self.pos_base = 0
        self.pipe_base = img_cano
        self.pipe_top = pygame.transform.flip(img_cano, False, True)
        self.passou = False
        self.gerar_altura()

    def gerar_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_top = self.altura - self.pipe_top.get_height()
        self.pos_base = self.altura + self.distancia

    def mover(self):
        self.x -= self.velocidade

    def desenhar(self, tela):
        tela.blit(self.pipe_top, (self.x, self.pos_top))
        tela.blit(self.pipe_base, (self.x, self.pos_base))

    def colidir(self, passaro):
        bird_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.pipe_top)
        base_mask = pygame.mask.from_surface(self.pipe_base)

        distancia_top = (self.x - passaro.x, self.pos_top - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        top_ponto = bird_mask.overlap(topo_mask, distancia_top)
        base_ponto = bird_mask.overlap(base_mask, distancia_base)

        return base_ponto or top_ponto


class Chao:
    velocidade = 5
    largura = img_chao.get_width()
    imagem = img_chao

    def __init__(self, y):
        self.y = y
        self.x0 = 0
        self.x1 = self.largura

    def mover(self):
        self.x0 -= self.velocidade
        self.x1 -= self.velocidade

        if self.x0 + self.largura < 0:
            self.x0 = self.largura

        if self.x1 + self.largura < 0:
            self.x1 = self.largura

    def desenhar(self, tela):
        tela.blit(self.imagem, (self.x0, self.y))
        tela.blit(self.imagem, (self.x1, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(img_background, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = font_pts.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (tela_largura - 10 - texto.get_width(), 10))
    chao.desenhar(tela)
    pygame.display.update()


def main():
    passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((tela_largura, tela_altura))
    pontos = 0
    relogio = pygame.time.Clock()
    rodando = True

    while rodando:
        relogio.tick(30)
        for evento in pygame.event.get():
            if evento.type == pygame.quit:
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    for passaro in passaros:
                        passaro.pular()

        for passaro in passaros:
            passaro.mover()
        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True

            cano.mover()

            if cano.x + cano.pipe_top.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))

        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagens.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)

        desenhar_tela(tela, passaros, canos, chao, pontos)

if __name__ == '__main__':
    main()
