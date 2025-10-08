-- Funcionamiento en el destino --

El servidor remoto debe ejecutar un script complementario que:

Reciba el .zip.

Verifique el hash SHA-256.

Descifre el contenido con la misma clave simétrica (AES-256-GCM).

Decodifique de Base64 y restaure el archivo original.

(Opcionalmente se puede automatizar con una tarea programada o daemon de verificación de integridad).


-- Seguridad y buenas prácticas --

La clave AES debe ser única por sesión o rotada periódicamente (cada 90 días).

El archivo .env debe tener permisos restringidos (chmod 600).

El script debe ejecutarse bajo usuario con privilegios mínimos.

Se recomienda mantener un Vault o HSM para gestionar las claves de forma centralizada.

Las transferencias deben registrarse en logs firmados digitalmente para auditoría.


-- Integración con las Políticas de Seguridad --

Este anexo se relaciona directamente con las políticas institucionales definidas:

Política de Gestión de Claves Criptográficas: el script no almacena contraseñas ni claves planas; usa variables seguras y soporta rotación.

Política de Transmisión Segura de Información: el canal SFTP/SSH está cifrado extremo a extremo; se evita el uso de canales inseguros (FTP/HTTP).


-- Resultado Esperado --

Al ejecutar el script:

El archivo queda cifrado, autenticado, comprimido y transferido automáticamente.

El destinatario puede verificar la integridad y autenticidad del envío con el hash SHA-256.

Todo el proceso se ejecuta sin intervención manual, cumpliendo la automatización completa solicitada por el proyecto.
