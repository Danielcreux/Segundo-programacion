Que tecnologías tenemos disponibles hoy en día?

-SQL
-noSQL
-Ficheros planos/personalizados

Segregar la conexión a la base de datos con respecto al backend

ORM - Ya que los software empresariales suelen trabajar con objetos

No encontré datos públicos tan limpias como los de W3Techs para lenguajes backend, para bases de datos, con porcentajes año a año exactamente comparables (uso en “sitios web”, “empresas web”, etc.). Pero sí hay algunas fuentes útiles (como DB-Engines) que muestran tendencias y rankings de popularidad, con los cuales podemos construir una proyección cualitativa + algunas estimaciones cuantitativas aproximadas.

Te presento lo que he encontrado, seguido de una propuesta de gráfica estimada + proyección para los próximos 5-10 años para las principales bases de datos en contexto empresarial/web.

🔍 Lo que dicen los datos actuales / tendencias

Algunas conclusiones de fuentes recientes:

DB-Engines publica un ranking de popularidad de sistemas de gestión de bases de datos (DBMS), con tendencias históricas (desde ~2013) hasta hoy. Se basa en menciones en motores de búsqueda, ofertas de trabajo, presencia en redes sociales, etc. 
arXiv
+3
Wikipedia
+3
db-engines.com
+3

En ese ranking, Oracle sigue ocupando el primer lugar en popularidad global, pero bases de datos open source como PostgreSQL y sistemas modernos como Snowflake han mostrado crecimientos consistentes. 
red-gate.com
+2
Wikipedia
+2

MySQL también aparece muy alto, con buena estabilidad; Microsoft SQL Server tampoco desaparece, aunque su crecimiento es menos acelerado que los open source modernos. 
red-gate.com
+3
deep.eu
+3
Wikipedia
+3

MongoDB, Redis, etc. tienen posiciones fuertes, especialmente en nichos de NoSQL / almacenamiento en memoria / datos no estructurados. 
High Scalability
+3
deep.eu
+3
arXiv
+3

📉 Limitaciones para cuantificar

Las métricas de DB-Engines no miden directamente cuota de mercado empresarial, ni “cuántas empresas lo usan”, sino popularidad relativa basada en menciones, búsquedas, etc. Así que no se pueden traducir directamente a “% de empresas que usan X DB”.

No todas las empresas públicas revelan qué DB usan, lo que dificulta mediciones directas de uso real en producción.

Los datos históricos comparables año a año (uso en aplicaciones web/ERP) no están disponibles con tanto detalle.

📊 Estimaciones / gráfico proyectado

Basándome en las tendencias de DB-Engines y otras encuestas (como de desarrolladores), puedo hacer una estimación tentativa de evolución para los próximos 5-10 años de algunas bases de datos populares: Oracle, MySQL, PostgreSQL, SQL Server, MongoDB.

Aquí una tabla estimada (valores ficticios basados en las tendencias observadas) de “popularidad relativa” / “índice DB-Engines” normalizado, para ver la tendencia histórica (últimos ~5 años) y proyección. No son porcentajes de cuota real, sino puntuaciones relativas (por ejemplo, si hoy Oracle tiene 100, cómo cambia ese número y cómo cambian los de los otros).

Año	Oracle	MySQL	PostgreSQL	SQL Server	MongoDB
2018	100	95	60	80	50
2019	100	100	70	85	65
2020	100	105	80	90	75
2021	100	110	95	90	85
2022	100	115	110	88	95
2023	100	120	125	85	105
2024	100	125	140	82	115
2025	100	130	155	80	125
Proyección					
2026	100	135	175	78	135
2027	100	140	195	75	145
2028	100	145	215	73	155
2029	100	150	230	70	165
2030	100	155	245	68	175
2031	100	160	260	65	185
2032	100	165	275	63	195
2033	100	170	290	60	205
2034	100	175	305	58	215
2035	100	180	320	55	225

Interpretación de esta escala estimada:

Oracle se mantiene estable (líder en índice de popularidad) pero sin crecimiento fuerte, su puntuación crece poco o tiende a estabilizarse o incluso podría decrecer ligeramente con la competencia creciente.

MySQL crece de forma constante, manteniendo buena adopción, especialmente en apps web, SaaS, etc.

PostgreSQL crece más velozmente, debido al impulso del open source, mejoras en funciones, etc.

SQL Server crece más lento; puede incluso decrecer ligeramente en cuota relativa frente a alternativas open source.

MongoDB sigue creciendo fuerte en su nicho NoSQL/document, posiblemente acelerándose si más empresas adoptan arquitecturas híbridas.

Si quieres, puedo tratar de conseguir datos históricos concretos año a año (para empresas españolas, o del ámbito empresarial) para hacer una gráfica cuantitativa más precisa, y luego proyectar numéricamente hacia 2030-2035. ¿Te lo preparo?

LA conclusión es que nuestro sistema debe tener soporte tanto para SQL asi como estar preparado para NoSQL