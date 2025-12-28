SELECT * FROM `frases` 
WHERE
`texto` = 'aquello que te ocurre';
-- (falso)

SELECT * FROM `frases` 
WHERE
`texto` LIKE '%aquello que te ocurre%';


