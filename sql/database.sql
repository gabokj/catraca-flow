-- Banco de dados para o Sistema de Controle de Catraca

CREATE DATABASE IF NOT EXISTS `controle_catraca`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `controle_catraca`;

-- Tabela de alunos
CREATE TABLE IF NOT EXISTS `alunos` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `cpf` VARCHAR(20) NOT NULL,
  `nome` VARCHAR(150) NOT NULL,
  `turma` VARCHAR(50) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_alunos_cpf` (`cpf`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de tickets gerados
CREATE TABLE IF NOT EXISTS `tickets` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `aluno_id` INT UNSIGNED NULL,
  `cpf` VARCHAR(20) NOT NULL,
  `motivo` VARCHAR(150) NOT NULL,
  `tipo` ENUM('entrada', 'saida', 'uniforme', 'cracha_esquecimento', 'cracha_perda', 'outro') NOT NULL,
  `qr_codigo` INT NOT NULL,
  `qr_instrucoes` TEXT NOT NULL,
  `data` DATE NOT NULL,
  `hora` TIME NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_tickets_cpf` (`cpf`),
  KEY `idx_tickets_aluno_id` (`aluno_id`),
  CONSTRAINT `fk_tickets_aluno` FOREIGN KEY (`aluno_id`) REFERENCES `alunos` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de ocorrências (esquecimento/perda/uniforme)
CREATE TABLE IF NOT EXISTS `ocorrencias` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `aluno_id` INT UNSIGNED NULL,
  `cpf` VARCHAR(20) NOT NULL,
  `tipo` ENUM('esquecimento', 'perda', 'uniforme') NOT NULL,
  `data` DATE NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_ocorrencias_cpf_tipo_data` (`cpf`, `tipo`, `data`),
  KEY `idx_ocorrencias_aluno_id` (`aluno_id`),
  CONSTRAINT `fk_ocorrencias_aluno` FOREIGN KEY (`aluno_id`) REFERENCES `alunos` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Alguns alunos de exemplo (opcional)
INSERT INTO `alunos` (`cpf`, `nome`, `turma`) VALUES
  ('123.456.789-00', 'Fulano Beltrano Sicrano', 'XAM')
ON DUPLICATE KEY UPDATE `nome` = VALUES(`nome`), `turma` = VALUES(`turma`);


