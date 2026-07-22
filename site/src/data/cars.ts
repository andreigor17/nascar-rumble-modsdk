// Gerado de docs/cars.csv (scripts/dump_cars.py). Roster de 32 carros.
export type Car = { name: string; number: number; rating: number; klass: number };
export const CARS: Car[] = [
  { name: 'Richard Petty', number: 43, rating: 63, klass: 40 },
  { name: 'Cale Yarborough', number: 11, rating: 62, klass: 30 },
  { name: 'David Pearson', number: 17, rating: 61, klass: 20 },
  { name: 'Benny Parsons', number: 72, rating: 60, klass: 20 },
  { name: 'Davey Allison', number: 28, rating: 59, klass: 30 },
  { name: 'Bobby Allison', number: 22, rating: 58, klass: 30 },
  { name: 'EA Sports Car', number: 153, rating: 58, klass: 45 },
  { name: 'Alan Kulwicki', number: 7, rating: 57, klass: 20 },
  { name: 'Dale Jarrett', number: 88, rating: 54, klass: 20 },
  { name: 'Rick Carelli', number: 6, rating: 50, klass: 20 },
  { name: 'Jeff Burton', number: 99, rating: 48, klass: 20 },
  { name: 'Scott Hansen', number: 52, rating: 48, klass: 30 },
  { name: 'Ron Hornaday', number: 16, rating: 45, klass: 10 },
  { name: 'Wally Dallenbach', number: 25, rating: 40, klass: 10 },
  { name: 'Mike Skinner', number: 31, rating: 40, klass: 10 },
  { name: 'Jack Sprague', number: 24, rating: 40, klass: 10 },
  { name: 'Ken Schrader', number: 33, rating: 35, klass: 10 },
  { name: 'Sterling Marlin', number: 40, rating: 35, klass: 10 },
  { name: 'John Andretti', number: 43, rating: 35, klass: 10 },
  { name: 'Kenny Wallace', number: 55, rating: 32, klass: 20 },
  { name: 'Johnny Benson', number: 26, rating: 30, klass: 10 },
  { name: 'Kenny Irwin Jr.', number: 28, rating: 30, klass: 10 },
  { name: 'Geoff Bodine', number: 60, rating: 30, klass: 20 },
  { name: 'Bill Elliott', number: 94, rating: 30, klass: 20 },
  { name: 'Mike Wallace', number: 2, rating: 30, klass: 10 },
  { name: 'Stacy Compton', number: 86, rating: 30, klass: 10 },
  { name: 'Ernie Irvan', number: 36, rating: 25, klass: 10 },
  { name: 'Joe Nemechek', number: 42, rating: 25, klass: 20 },
  { name: 'Kyle Petty', number: 44, rating: 25, klass: 10 },
  { name: 'Darrell Waltrip', number: 66, rating: 25, klass: 30 },
  { name: 'Adam Petty', number: 45, rating: 20, klass: 10 },
  { name: 'Chad Little', number: 97, rating: 20, klass: 10 },
];

export type Livery = { src: string; pt: string; en: string; roster: boolean };
export const LIVERIES: Livery[] = [
  { src: '/cars/petty-43.png', pt: 'Richard Petty — #43 (EXIDE). No roster.', en: 'Richard Petty — #43 (EXIDE). In the roster.', roster: true },
  { src: '/cars/compton-86.png', pt: 'Stacy Compton — #86 (Royal Crown). No roster.', en: 'Stacy Compton — #86 (Royal Crown). In the roster.', roster: true },
  { src: '/cars/gordon-24.png', pt: 'Jeff Gordon — #24 (DuPont). Livery extra do disco.', en: 'Jeff Gordon — #24 (DuPont). Bonus livery on the disc.', roster: false },
  { src: '/cars/labonte-5.png', pt: 'Terry Labonte — #5 (Kellogg\'s). Livery extra do disco.', en: 'Terry Labonte — #5 (Kellogg\'s). Bonus livery on the disc.', roster: false },
];
