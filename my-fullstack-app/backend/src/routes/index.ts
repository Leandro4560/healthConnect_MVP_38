export const setRoutes = (app) => {
    const exampleController = new (require('../controllers/exampleController')).ExampleController();

    app.get('/api/example', exampleController.getExample);
    app.post('/api/example', exampleController.createExample);
};