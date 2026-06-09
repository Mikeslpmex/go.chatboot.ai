"""
╔══════════════════════════════════════════════════════════════════════╗
║  🔗 NEURAFORGE AWS CONNECTOR                                         ║
║  Módulo de conexión y ejecución de código en Amazon AWS             ║
║  Soporta: Lambda, EC2 (SSM), ECS, S3, RDS                          ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import boto3
import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

# ============================================================================
# CONFIGURACIÓN Y LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AWSConfig:
    """Configuración de AWS"""
    access_key_id: str = os.getenv('AWS_ACCESS_KEY_ID', '')
    secret_access_key: str = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    region: str = os.getenv('AWS_REGION', 'us-east-1')
    session_token: Optional[str] = os.getenv('AWS_SESSION_TOKEN', None)
    
    def validate(self) -> bool:
        """Valida que las credenciales existan"""
        if not self.access_key_id or not self.secret_access_key:
            logger.error("❌ Credenciales de AWS no configuradas")
            return False
        return True


# ============================================================================
# CLASE PRINCIPAL: AWS CONNECTOR
# ============================================================================

class AWSConnector:
    """
    Conector universal para AWS
    Maneja autenticación, sesiones y ejecución de comandos
    """
    
    def __init__(self, config: Optional[AWSConfig] = None):
        """
        Inicializa el conector AWS
        
        Args:
            config: Configuración personalizada (opcional)
        """
        self.config = config or AWSConfig()
        
        if not self.config.validate():
            raise ValueError("Credenciales de AWS inválidas")
        
        self.session = boto3.Session(
            aws_access_key_id=self.config.access_key_id,
            aws_secret_access_key=self.config.secret_access_key,
            aws_session_token=self.config.session_token,
            region_name=self.config.region
        )
        
        logger.info(f"✅ Sesión AWS iniciada en región: {self.config.region}")
    
    # ========================================================================
    # LAMBDA - Ejecución sin servidor
    # ========================================================================
    
    def invoke_lambda(
        self,
        function_name: str,
        payload: Dict[str, Any],
        async_invoke: bool = False
    ) -> Dict[str, Any]:
        """
        Invoca una función Lambda
        
        Args:
            function_name: Nombre de la función Lambda
            payload: Datos a enviar (dict)
            async_invoke: True para ejecución asíncrona
            
        Returns:
            Respuesta de la función Lambda
            
        Ejemplo:
            connector = AWSConnector()
            response = connector.invoke_lambda(
                'my-function',
                {'action': 'process', 'data': 'test'}
            )
        """
        try:
            lambda_client = self.session.client('lambda')
            
            invocation_type = 'Event' if async_invoke else 'RequestResponse'
            
            logger.info(f"🚀 Invocando Lambda: {function_name}")
            
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType=invocation_type,
                Payload=json.dumps(payload)
            )
            
            # Procesar respuesta
            if response['StatusCode'] == 200:
                logger.info(f"✅ Lambda invocada exitosamente")
                
                if invocation_type == 'RequestResponse':
                    response_payload = json.loads(
                        response['Payload'].read().decode('utf-8')
                    )
                    return {
                        'success': True,
                        'status_code': response['StatusCode'],
                        'data': response_payload
                    }
                else:
                    return {
                        'success': True,
                        'status_code': response['StatusCode'],
                        'message': 'Ejecución asíncrona iniciada'
                    }
            else:
                logger.error(f"❌ Error Lambda: {response['StatusCode']}")
                return {
                    'success': False,
                    'status_code': response['StatusCode'],
                    'error': response.get('FunctionError', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"❌ Error invocando Lambda: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========================================================================
    # EC2 + SSM - Ejecutar comandos en instancias EC2
    # ========================================================================
    
    def execute_on_ec2(
        self,
        instance_id: str,
        commands: List[str],
        wait_for_completion: bool = True,
        timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Ejecuta comandos shell en una instancia EC2 usando SSM
        
        Args:
            instance_id: ID de la instancia EC2 (ej: i-0123456789abcdef0)
            commands: Lista de comandos a ejecutar
            wait_for_completion: Esperar a que termine
            timeout_seconds: Timeout para ejecución
            
        Returns:
            Resultado de la ejecución
            
        Ejemplo:
            response = connector.execute_on_ec2(
                'i-0123456789abcdef0',
                ['echo "Hola AWS"', 'python script.py']
            )
        """
        try:
            ssm_client = self.session.client('ssm')
            
            logger.info(f"📤 Ejecutando comandos en EC2: {instance_id}")
            
            # Enviar comando
            response = ssm_client.send_command(
                InstanceIds=[instance_id],
                DocumentName='AWS-RunShellScript',
                Parameters={'commands': commands},
                TimeoutSeconds=[timeout_seconds]
            )
            
            command_id = response['Command']['CommandId']
            logger.info(f"📋 Command ID: {command_id}")
            
            if wait_for_completion:
                return self._wait_for_command(ssm_client, command_id, instance_id)
            else:
                return {
                    'success': True,
                    'command_id': command_id,
                    'message': 'Comando enviado (ejecución asíncrona)'
                }
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando en EC2: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _wait_for_command(
        self,
        ssm_client,
        command_id: str,
        instance_id: str,
        max_attempts: int = 60
    ) -> Dict[str, Any]:
        """
        Espera a que se complete un comando SSM
        """
        import time
        
        for attempt in range(max_attempts):
            try:
                response = ssm_client.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=instance_id
                )
                
                status = response['Status']
                
                if status in ['Success', 'Failed', 'Cancelled']:
                    output = response.get('StandardOutputContent', '')
                    error = response.get('StandardErrorContent', '')
                    
                    logger.info(f"✅ Comando completado: {status}")
                    
                    return {
                        'success': status == 'Success',
                        'status': status,
                        'output': output,
                        'error': error,
                        'command_id': command_id
                    }
                
                logger.info(f"⏳ Estado: {status}... ({attempt + 1}/{max_attempts})")
                time.sleep(2)
                
            except ssm_client.exceptions.InvocationDoesNotExist:
                logger.warning("⏳ Comando aún procesándose...")
                time.sleep(2)
        
        return {
            'success': False,
            'error': 'Timeout esperando comando',
            'command_id': command_id
        }
    
    # ========================================================================
    # ECS - Ejecutar tareas en contenedores
    # ========================================================================
    
    def run_ecs_task(
        self,
        cluster: str,
        task_definition: str,
        container_name: str,
        command: Optional[List[str]] = None,
        environment: Optional[Dict[str, str]] = None,
        launch_type: str = 'FARGATE'
    ) -> Dict[str, Any]:
        """
        Ejecuta una tarea en ECS (Elastic Container Service)
        
        Args:
            cluster: Nombre del cluster ECS
            task_definition: Definición de tarea
            container_name: Nombre del contenedor
            command: Comando a ejecutar (sobrescribe el del contenedor)
            environment: Variables de entorno
            launch_type: FARGATE o EC2
            
        Ejemplo:
            response = connector.run_ecs_task(
                cluster='my-cluster',
                task_definition='my-task:1',
                container_name='app',
                command=['python', 'script.py']
            )
        """
        try:
            ecs_client = self.session.client('ecs')
            
            logger.info(f"🐳 Ejecutando tarea ECS: {task_definition}")
            
            run_task_kwargs = {
                'cluster': cluster,
                'taskDefinition': task_definition,
                'launchType': launch_type,
            }
            
            # Agregar comando si se proporciona
            if command:
                run_task_kwargs['overrides'] = {
                    'containerOverrides': [
                        {
                            'name': container_name,
                            'command': command,
                            'environment': [
                                {'name': k, 'value': v}
                                for k, v in (environment or {}).items()
                            ]
                        }
                    ]
                }
            
            response = ecs_client.run_task(**run_task_kwargs)
            
            if response['tasks']:
                task_arn = response['tasks'][0]['taskArn']
                logger.info(f"✅ Tarea iniciada: {task_arn}")
                
                return {
                    'success': True,
                    'task_arn': task_arn,
                    'task_id': task_arn.split('/')[-1],
                    'status': response['tasks'][0]['lastStatus']
                }
            else:
                logger.error(f"❌ Error iniciando tarea ECS")
                return {
                    'success': False,
                    'error': response.get('failures', [{}])[0].get('reason', 'Unknown')
                }
                
        except Exception as e:
            logger.error(f"❌ Error en ECS: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========================================================================
    # S3 - Operaciones con almacenamiento
    # ========================================================================
    
    def upload_to_s3(
        self,
        file_path: str,
        bucket: str,
        key: str
    ) -> Dict[str, Any]:
        """
        Sube un archivo a S3
        
        Args:
            file_path: Ruta local del archivo
            bucket: Nombre del bucket S3
            key: Clave/path en S3
        """
        try:
            s3_client = self.session.client('s3')
            
            logger.info(f"📤 Subiendo a S3: {key}")
            
            s3_client.upload_file(file_path, bucket, key)
            
            logger.info(f"✅ Archivo subido exitosamente")
            
            return {
                'success': True,
                'bucket': bucket,
                'key': key,
                'url': f"s3://{bucket}/{key}"
            }
            
        except Exception as e:
            logger.error(f"❌ Error subiendo a S3: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def download_from_s3(
        self,
        bucket: str,
        key: str,
        file_path: str
    ) -> Dict[str, Any]:
        """Descarga un archivo de S3"""
        try:
            s3_client = self.session.client('s3')
            
            logger.info(f"📥 Descargando desde S3: {key}")
            
            s3_client.download_file(bucket, key, file_path)
            
            logger.info(f"✅ Archivo descargado exitosamente")
            
            return {
                'success': True,
                'file_path': file_path,
                'bucket': bucket,
                'key': key
            }
            
        except Exception as e:
            logger.error(f"❌ Error descargando de S3: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========================================================================
    # RDS - Conexión a bases de datos
    # ========================================================================
    
    def get_rds_connection(
        self,
        db_instance_id: str
    ) -> Dict[str, Any]:
        """
        Obtiene información de conexión a RDS
        
        Args:
            db_instance_id: ID de la instancia RDS
            
        Retorna datos para conectarse con pymysql, psycopg2, etc.
        """
        try:
            rds_client = self.session.client('rds')
            
            response = rds_client.describe_db_instances(
                DBInstanceIdentifier=db_instance_id
            )
            
            if response['DBInstances']:
                db = response['DBInstances'][0]
                
                connection_info = {
                    'success': True,
                    'host': db['Endpoint']['Address'],
                    'port': db['Endpoint']['Port'],
                    'engine': db['Engine'],
                    'database': db.get('DBName', ''),
                    'username': db['MasterUsername'],
                    'status': db['DBInstanceStatus']
                }
                
                logger.info(f"✅ Información RDS obtenida: {db_instance_id}")
                
                return connection_info
            else:
                return {'success': False, 'error': 'Base de datos no encontrada'}
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo RDS: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========================================================================
    # UTILIDADES
    # ========================================================================
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica la conexión a AWS"""
        try:
            sts_client = self.session.client('sts')
            identity = sts_client.get_caller_identity()
            
            logger.info(f"✅ AWS Health Check OK")
            
            return {
                'success': True,
                'account_id': identity['Account'],
                'user_arn': identity['Arn'],
                'region': self.config.region,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Health check fallido: {str(e)}")
            return {'success': False, 'error': str(e)}


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def create_connector(
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    region: Optional[str] = None
) -> AWSConnector:
    """
    Crea un conector AWS de forma simplificada
    
    Si no se proporcionan credenciales, usa las del .env
    """
    config = AWSConfig(
        access_key_id=access_key or os.getenv('AWS_ACCESS_KEY_ID', ''),
        secret_access_key=secret_key or os.getenv('AWS_SECRET_ACCESS_KEY', ''),
        region=region or os.getenv('AWS_REGION', 'us-east-1')
    )
    
    return AWSConnector(config)


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("🔗 NeuraforgeAI AWS Connector")
    print("=" * 50)
    
    try:
        # Crear conector
        connector = create_connector()
        
        # Health check
        print("\n📊 Health Check:")
        health = connector.health_check()
        print(json.dumps(health, indent=2))
        
        # Ejemplo: Invocar Lambda
        print("\n⚡ Ejemplo Lambda:")
        print("connector.invoke_lambda('my-function', {'key': 'value'})")
        
        # Ejemplo: Ejecutar en EC2
        print("\n💻 Ejemplo EC2:")
        print("connector.execute_on_ec2('i-xxxxx', ['echo hello'])")
        
        # Ejemplo: Ejecutar en ECS
        print("\n🐳 Ejemplo ECS:")
        print("connector.run_ecs_task('cluster', 'task:1', 'container')")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\n📝 Asegúrate de configurar en .env:")
        print("AWS_ACCESS_KEY_ID=xxx")
        print("AWS_SECRET_ACCESS_KEY=xxx")
        print("AWS_REGION=us-east-1")
