INSERT INTO animals (name, species, breed, owner_name, owner_phone, birth_date)
VALUES
('Thor', 'Cachorro', 'Golden Retriever', 'Mariana Souza', '(18) 99999-1111', '2021-05-10'),
('Luna', 'Gato', 'Siamês', 'Carlos Lima', '(18) 98888-2222', '2022-08-15'),
('Mel', 'Cachorro', 'Shih-tzu', 'Ana Ribeiro', '(18) 97777-3333', '2020-11-03');

INSERT INTO services (animal_id, service_type, description, service_date, veterinarian, price)
VALUES
(1, 'Consulta', 'Consulta de rotina e avaliação geral.', '2026-08-20', 'Dra. Camila', 120.00),
(1, 'Vacina', 'Aplicação de vacina anual V10.', '2026-08-20', 'Dra. Camila', 95.00),
(2, 'Exame', 'Hemograma completo para avaliação preventiva.', '2026-08-25', 'Dr. Rafael', 85.00),
(3, 'Consulta', 'Avaliação dermatológica.', '2026-08-28', 'Dra. Camila', 120.00);
