import { Col, Row, Container, Navbar, Form } from "react-bootstrap";

export default function Home() {
  const handleSubmit = () => {
    alert("test");
  };

  return (
    <>
      <Navbar bg="dark" variant="dark">
        <Navbar.Brand>clue</Navbar.Brand>
      </Navbar>
      <Container fluid>
        <Row>
          <Col>
            <Form noValidate onSubmit={handleSubmit}>
              <Form.Row>
                <Col>
                  <Form.Group>
                    <Form.Label>me</Form.Label>
                    <Form.Control as="select">
                      <option>1</option>
                      <option>2</option>
                      <option>3</option>
                      <option>4</option>
                      <option>5</option>
                    </Form.Control>
                  </Form.Group>
                </Col>
                <Col>
                  <Form.Group>
                    <Form.Label>cards</Form.Label>
                    <Form.Control as="select" multiple>
                      <option>1</option>
                      <option>2</option>
                      <option>3</option>
                      <option>4</option>
                      <option>5</option>
                    </Form.Control>
                  </Form.Group>
                </Col>
              </Form.Row>
            </Form>
          </Col>
          <Col sm={5}></Col>
        </Row>
      </Container>
    </>
  );
}
