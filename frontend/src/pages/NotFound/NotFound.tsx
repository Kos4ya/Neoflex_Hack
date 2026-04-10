import './not-found.css'

export const NotFound = () => {
  return (
    <div className='not-found'>
      <h1 className='not-found__title'>404</h1>
      <p className='not-found__description'>Страница не найдена</p>
      <p className='not-found__hint'>
        Формат ссылки: <code className="not-found__code">/interview/:roomId</code>
      </p>
    </div>
  );
}