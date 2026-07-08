from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class TestItAsset(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Configurar datos comunes para todos los tests."""
        super().setUpClass()
        
        # Crear categoría
        cls.category = cls.env['it.asset.category'].create({
            'name': 'Laptops',
            'code': 'LTP',
        })
        
        # Crear empleados de prueba
        cls.employee_1 = cls.env['hr.employee'].create({
            'name': 'Test Employee 1',
        })
        cls.employee_2 = cls.env['hr.employee'].create({
            'name': 'Test Employee 2',
        })

    def test_01_create_asset_with_default_state(self):
        """Test 1: Creación de activo con estado por defecto disponible."""
        asset = self.env['it.asset'].create({
            'name': 'Test Laptop',
            'asset_type': 'laptop',
            'serial_number': 'TEST-001',
            'category_id': self.category.id,
        })
        
        self.assertEqual(asset.state, 'disponible')
        self.assertIsNone(asset.current_employee_id)

    def test_02_assign_asset_success(self):
        """Test 2: Asignación exitosa cambia estado y crea registro de asignación."""
        asset = self.env['it.asset'].create({
            'name': 'Test Laptop 2',
            'asset_type': 'laptop',
            'serial_number': 'TEST-002',
            'category_id': self.category.id,
        })
        
        # Crear asignación
        assignment = self.env['it.asset.assignment'].create({
            'asset_id': asset.id,
            'employee_id': self.employee_1.id,
        })
        
        # Verificar que el estado cambió a asignado
        self.assertEqual(asset.state, 'asignado')
        # Verificar que el empleado actual es el asignado
        self.assertEqual(asset.current_employee_id, self.employee_1)
        # Verificar que el registro de asignación existe
        self.assertIn(assignment, asset.assignment_ids)

    def test_03_assign_already_assigned_asset_fails(self):
        """Test 3: Intentar asignar un activo ya asignado lanza ValidationError."""
        asset = self.env['it.asset'].create({
            'name': 'Test Laptop 3',
            'asset_type': 'laptop',
            'serial_number': 'TEST-003',
            'category_id': self.category.id,
        })
        
        # Primer asignación
        self.env['it.asset.assignment'].create({
            'asset_id': asset.id,
            'employee_id': self.employee_1.id,
        })
        
        # Intentar segunda asignación sin devolver primero
        with self.assertRaises(ValidationError):
            self.env['it.asset.assignment'].create({
                'asset_id': asset.id,
                'employee_id': self.employee_2.id,
            })

    def test_04_return_asset(self):
        """Test 4: Devolver un activo asignado cierra la asignación y vuelve a disponible."""
        asset = self.env['it.asset'].create({
            'name': 'Test Laptop 4',
            'asset_type': 'laptop',
            'serial_number': 'TEST-004',
            'category_id': self.category.id,
        })
        
        # Asignar
        assignment = self.env['it.asset.assignment'].create({
            'asset_id': asset.id,
            'employee_id': self.employee_1.id,
        })
        
        self.assertEqual(asset.state, 'asignado')
        
        # Devolver
        asset.action_return()
        
        self.assertEqual(asset.state, 'disponible')
        self.assertIsNone(asset.current_employee_id)
        # Verificar que la asignación tiene fecha de devolución
        self.assertIsNotNone(assignment.returned_date)

    def test_05_retire_asset_with_active_assignment_fails(self):
        """Test 5: No se puede dar de baja un activo con asignación activa."""
        asset = self.env['it.asset'].create({
            'name': 'Test Laptop 5',
            'asset_type': 'laptop',
            'serial_number': 'TEST-005',
            'category_id': self.category.id,
        })
        
        # Asignar
        self.env['it.asset.assignment'].create({
            'asset_id': asset.id,
            'employee_id': self.employee_1.id,
        })
        
        # Intentar dar de baja
        with self.assertRaises(ValidationError):
            asset.action_retire()

    def test_06_assignment_history_correct(self):
        """Test 6: Historial de asignaciones correcto tras múltiples ciclos."""
        asset = self.env['it.asset'].create({
            'name': 'Test Laptop 6',
            'asset_type': 'laptop',
            'serial_number': 'TEST-006',
            'category_id': self.category.id,
        })
        
        # Primera asignación
        assignment_1 = self.env['it.asset.assignment'].create({
            'asset_id': asset.id,
            'employee_id': self.employee_1.id,
        })
        self.assertEqual(len(asset.assignment_ids), 1)
        
        # Devolver
        asset.action_return()
        self.assertIsNotNone(assignment_1.returned_date)
        
        # Segunda asignación
        assignment_2 = self.env['it.asset.assignment'].create({
            'asset_id': asset.id,
            'employee_id': self.employee_2.id,
        })
        self.assertEqual(len(asset.assignment_ids), 2)
        
        # Devolver de nuevo
        asset.action_return()
        self.assertIsNotNone(assignment_2.returned_date)
        
        # Verificar que ambas asignaciones están cerradas
        for assignment in asset.assignment_ids:
            self.assertIsNotNone(assignment.returned_date)
