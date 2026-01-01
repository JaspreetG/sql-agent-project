CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    salary INTEGER,
    join_date DATE
);

INSERT INTO employees (name, department, salary, join_date) VALUES 
('Alice', 'IT', 120000, '2020-01-15'),
('Bob', 'IT', 85000, '2021-06-01'),
('Charlie', 'HR', 60000, '2019-11-20'),
('Dave', 'Finance', 95000, '2018-03-10'),
('Eve', 'IT', 110000, '2022-08-15');