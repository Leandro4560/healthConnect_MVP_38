class ExampleController {
    public async getExample(req, res) {
        try {
            // Lógica para manejar la solicitud GET
            res.status(200).json({ message: "Ejemplo obtenido correctamente" });
        } catch (error) {
            res.status(500).json({ error: "Error al obtener el ejemplo" });
        }
    }

    public async createExample(req, res) {
        try {
            // Lógica para manejar la solicitud POST
            res.status(201).json({ message: "Ejemplo creado correctamente" });
        } catch (error) {
            res.status(500).json({ error: "Error al crear el ejemplo" });
        }
    }

    // Puedes agregar más métodos según sea necesario
}

export default ExampleController;