# Incidencias — DeepSeek FASE 10

La suite completa fallaba por contaminación de `app.dependency_overrides[get_db]`. Se corrigió moviendo overrides a `setUpClass()` y limpiándolos en `tearDownClass()`.
