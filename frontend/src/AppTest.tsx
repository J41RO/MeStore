// React import removido - no necesario con react-jsx

function AppTest() {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>🔐 MeStore Test</h1>
      <p>Si ves este mensaje, React está funcionando</p>
      <button onClick={() => alert('¡Funciona!')}>
        Probar JavaScript
      </button>
    </div>
  )
}

export default AppTest
