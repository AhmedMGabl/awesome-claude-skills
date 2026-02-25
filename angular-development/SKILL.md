---
name: angular-development
description: This skill should be used when building Angular 18+ applications with signals, standalone components, new control flow syntax (@if/@for/@switch), defer blocks, SSR with hydration, NgRx signal store, reactive forms, HTTP client with interceptors, routing with guards and resolvers, dependency injection, pipes, directives, Angular Material, testing with Jest and Cypress, lazy loading, and i18n.
---

# Angular Development

Apply this skill for all Angular 18+ development: standalone components with signals, NgRx SignalStore, routing, reactive forms, HTTP client, SSR, testing, and Angular Material. Use TypeScript throughout.

## Project Setup

```bash
ng new my-app --style=scss --ssr
cd my-app
npm install @ngrx/signals @angular/material @angular/cdk
npm install -D jest @types/jest jest-preset-angular cypress
```

## Standalone Components with Signals

```typescript
import { Component, input, output, computed, signal, effect, inject } from '@angular/core';

@Component({
  selector: 'app-user-card',
  standalone: true,
  template: `
    <article (click)="selected.emit(user().id)">
      <h3>{{ user().name }}</h3>
      <span [class]="'badge-' + user().role">{{ user().role }}</span>
      @if (showActions()) {
        <button (click)="deleted.emit(user().id); $event.stopPropagation()">Delete</button>
      }
    </article>
  `,
})
export class UserCardComponent {
  user = input.required<{ id: number; name: string; role: string }>();
  showActions = input(true);
  selected = output<number>();
  deleted = output<number>();
}

// signal(), computed(), effect()
@Component({
  selector: 'app-counter', standalone: true,
  template: `<p>{{ count() }} (x2: {{ doubled() }})</p>
    <button (click)="count.update(c => c + 1)">+1</button>`,
})
export class CounterComponent {
  count = signal(0);
  doubled = computed(() => this.count() * 2);
  constructor() { effect(() => console.log('Count:', this.count())); }
}
```

## New Control Flow

```html
@if (user(); as u) {
  <app-user-card [user]="u" />
} @else if (loading()) {
  <app-skeleton />
} @else {
  <p>No user found.</p>
}

@for (item of items(); track item.id) {
  <app-item-card [item]="item" />
} @empty {
  <p>No items available.</p>
}

@switch (status()) {
  @case ('active') { <span class="green">Active</span> }
  @case ('inactive') { <span class="red">Inactive</span> }
  @default { <span>Unknown</span> }
}
```

## Defer Blocks

```html
@defer (on viewport) {
  <app-heavy-chart [data]="chartData()" />
} @loading (minimum 200ms) {
  <app-spinner />
} @placeholder {
  <div>Chart loads on scroll</div>
}

@defer (on interaction; prefetch on idle) {
  <app-comments [postId]="postId()" />
} @placeholder {
  <button>Load Comments</button>
}

@defer (when isAdmin()) { <app-admin-panel /> }
```

## NgRx SignalStore

```typescript
import { computed, inject } from '@angular/core';
import { signalStore, withState, withComputed, withMethods, patchState, withHooks } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { tapResponse } from '@ngrx/operators';
import { pipe, switchMap, tap } from 'rxjs';

export const UsersStore = signalStore(
  { providedIn: 'root' },
  withState({ users: [] as { id: number; name: string }[], loading: false, error: null as string | null, filter: '' }),
  withComputed((s) => ({
    filteredUsers: computed(() => {
      const f = s.filter().toLowerCase();
      return f ? s.users().filter(u => u.name.toLowerCase().includes(f)) : s.users();
    }),
    userCount: computed(() => s.users().length),
  })),
  withMethods((store, svc = inject(UsersService)) => ({
    setFilter(filter: string) { patchState(store, { filter }); },
    removeUser(id: number) { patchState(store, { users: store.users().filter(u => u.id !== id) }); },
    loadUsers: rxMethod<void>(pipe(
      tap(() => patchState(store, { loading: true })),
      switchMap(() => svc.getAll().pipe(tapResponse({
        next: (users) => patchState(store, { users, loading: false }),
        error: (e: Error) => patchState(store, { error: e.message, loading: false }),
      }))),
    )),
  })),
  withHooks({ onInit(store) { store.loadUsers(); } }),
);
```

## Reactive Forms

```typescript
import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

@Component({
  selector: 'app-register', standalone: true, imports: [ReactiveFormsModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <input formControlName="name" />
      @if (form.controls.name.errors?.['required'] && form.controls.name.touched) {
        <span class="error">Required</span>
      }
      <input formControlName="email" type="email" />
      <input formControlName="password" type="password" />
      <button type="submit" [disabled]="form.invalid">Register</button>
    </form>
  `,
})
export class RegisterComponent {
  private fb = inject(FormBuilder);
  form = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });
  onSubmit() { if (this.form.valid) console.log(this.form.getRawValue()); }
}
```

## HTTP Client with Interceptors

```typescript
@Injectable({ providedIn: 'root' })
export class UsersService {
  private http = inject(HttpClient);
  getAll() { return this.http.get<any[]>('/api/users'); }
  getById(id: number) { return this.http.get<any>(`/api/users/${id}`); }
  create(user: any) { return this.http.post<any>('/api/users', user); }
  delete(id: number) { return this.http.delete<void>(`/api/users/${id}`); }
}

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = inject(AuthService).getToken();
  return next(token ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : req);
};

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  return next(req).pipe(catchError(err => {
    if (err.status === 401) router.navigate(['/login']);
    return throwError(() => err);
  }));
};

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor, errorInterceptor])),
    provideClientHydration(withEventReplay()),
    provideAnimationsAsync(),
  ],
};
```

## Routing with Guards, Resolvers, and Lazy Loading

```typescript
const authGuard = () => {
  const auth = inject(AuthService), router = inject(Router);
  return auth.isAuthenticated() ? true : router.createUrlTree(['/login']);
};
const adminGuard = () => inject(AuthService).currentUser()?.role === 'admin';
const userResolver = (route: any) => inject(UsersService).getById(+route.paramMap.get('id'));

export const routes: Routes = [
  { path: '', loadComponent: () => import('./pages/home.component').then(m => m.HomeComponent) },
  { path: 'login', loadComponent: () => import('./pages/login.component').then(m => m.LoginComponent) },
  { path: 'dashboard', canActivate: [() => authGuard()],
    loadChildren: () => import('./pages/dashboard/routes').then(m => m.DASHBOARD_ROUTES) },
  { path: 'admin', canActivate: [() => authGuard(), () => adminGuard()],
    loadComponent: () => import('./pages/admin.component').then(m => m.AdminComponent) },
  { path: 'users/:id', canActivate: [() => authGuard()], resolve: { user: userResolver },
    loadComponent: () => import('./pages/user-detail.component').then(m => m.UserDetailComponent) },
  { path: '**', loadComponent: () => import('./pages/not-found.component').then(m => m.NotFoundComponent) },
];

// Nested lazy routes: pages/dashboard/routes.ts
export const DASHBOARD_ROUTES: Routes = [
  { path: '', loadComponent: () => import('./overview.component').then(m => m.OverviewComponent) },
  { path: 'analytics', loadComponent: () => import('./analytics.component').then(m => m.AnalyticsComponent) },
];
```

## Dependency Injection

```typescript
export interface AppConfig { apiUrl: string; featureFlags: Record<string, boolean> }
export const APP_CONFIG = new InjectionToken<AppConfig>('app.config');
// Register: { provide: APP_CONFIG, useValue: { apiUrl: '/api', featureFlags: {} } }

@Injectable({ providedIn: 'root' })
export class ApiService {
  private config = inject(APP_CONFIG);
  private http = inject(HttpClient);
  get<T>(path: string) { return this.http.get<T>(`${this.config.apiUrl}${path}`); }
}
```

## Custom Pipe and Directive

```typescript
@Pipe({ name: 'timeAgo', standalone: true })
export class TimeAgoPipe implements PipeTransform {
  transform(value: string | Date): string {
    const s = Math.floor((Date.now() - new Date(value).getTime()) / 1000);
    for (const [sec, lbl] of [[31536000,'year'],[2592000,'month'],[86400,'day'],[3600,'hour'],[60,'min']] as const) {
      const n = Math.floor(s / sec);
      if (n >= 1) return `${n} ${lbl}${n > 1 ? 's' : ''} ago`;
    }
    return 'just now';
  }
} // {{ createdAt | timeAgo }}

@Directive({ selector: '[appHighlight]', standalone: true })
export class HighlightDirective {
  private el = inject(ElementRef);
  appHighlight = input('yellow');
  constructor() { effect(() => { this.el.nativeElement.style.backgroundColor = this.appHighlight(); }); }
} // <p [appHighlight]="color()">Text</p>
```

## Angular Material

```typescript
@Component({
  selector: 'app-users-table', standalone: true,
  imports: [MatTableModule, MatPaginatorModule, MatSortModule, MatInputModule],
  template: `
    <mat-form-field><mat-label>Filter</mat-label>
      <input matInput (input)="store.setFilter($any($event.target).value)" />
    </mat-form-field>
    <table mat-table [dataSource]="store.filteredUsers()" matSort>
      <ng-container matColumnDef="name">
        <th mat-header-cell *matHeaderCellDef mat-sort-header>Name</th>
        <td mat-cell *matCellDef="let row">{{ row.name }}</td>
      </ng-container>
      <ng-container matColumnDef="email">
        <th mat-header-cell *matHeaderCellDef mat-sort-header>Email</th>
        <td mat-cell *matCellDef="let row">{{ row.email }}</td>
      </ng-container>
      <tr mat-header-row *matHeaderRowDef="['name','email']"></tr>
      <tr mat-row *matRowDef="let row; columns: ['name','email']"></tr>
    </table>
    <mat-paginator [length]="store.userCount()" [pageSize]="10" [pageSizeOptions]="[5,10,25]" />
  `,
})
export class UsersTableComponent { readonly store = inject(UsersStore); }
```

## SSR with Hydration

```typescript
// app.config.server.ts -- merge server providers with client config
import { mergeApplicationConfig } from '@angular/core';
import { provideServerRendering } from '@angular/platform-server';
import { provideServerRouting } from '@angular/ssr';
export const config = mergeApplicationConfig(appConfig, {
  providers: [provideServerRendering(), provideServerRouting(serverRoutes)],
});

// app.routes.server.ts -- render strategy per route
import { RenderMode, ServerRoute } from '@angular/ssr';
export const serverRoutes: ServerRoute[] = [
  { path: '', renderMode: RenderMode.Prerender },        // Static at build
  { path: 'dashboard/**', renderMode: RenderMode.Client }, // SPA (no SSR)
  { path: '**', renderMode: RenderMode.Server },           // SSR on request
];
```

## Testing with Jest

```typescript
// Component test
describe('UserCardComponent', () => {
  let fixture: ComponentFixture<UserCardComponent>;
  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [UserCardComponent] }).compileComponents();
    fixture = TestBed.createComponent(UserCardComponent);
    fixture.componentRef.setInput('user', { id: 1, name: 'Alice', role: 'admin' });
    fixture.detectChanges();
  });
  it('displays user name', () => expect(fixture.nativeElement.textContent).toContain('Alice'));
  it('emits selected on click', () => {
    const spy = jest.fn();
    fixture.componentInstance.selected.subscribe(spy);
    fixture.nativeElement.querySelector('article').click();
    expect(spy).toHaveBeenCalledWith(1);
  });
});

// Service test with HttpTestingController
describe('UsersService', () => {
  let service: UsersService, httpMock: HttpTestingController;
  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(UsersService);
    httpMock = TestBed.inject(HttpTestingController);
  });
  afterEach(() => httpMock.verify());
  it('fetches users', () => {
    service.getAll().subscribe(u => expect(u.length).toBe(1));
    httpMock.expectOne('/api/users').flush([{ id: 1, name: 'Alice' }]);
  });
});
```

## E2E Testing with Cypress

```typescript
describe('Users Page', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/users*', { fixture: 'users.json' }).as('getUsers');
    cy.visit('/dashboard/users');
    cy.wait('@getUsers');
  });
  it('displays and filters users', () => {
    cy.get('app-user-card').should('have.length.greaterThan', 0);
    cy.get('input[placeholder="Filter users..."]').type('Alice');
    cy.get('app-user-card').should('have.length', 1).first().should('contain.text', 'Alice');
  });
});
```

## Internationalization (i18n)

Mark templates: `<h1 i18n="@@welcomeHeading">Welcome, {{ username }}</h1>`

```bash
ng extract-i18n --output-path src/locale   # Extract translatable strings
ng build --localize                         # Build all locales
ng serve --configuration=fr                 # Dev-serve a specific locale
```

angular.json: `{ "i18n": { "sourceLocale": "en", "locales": { "fr": "src/locale/messages.fr.xlf" } } }`

## File Organization

```
src/app/
├── app.config.ts / app.routes.ts / app.routes.server.ts
├── components/       # Shared UI and layout components
├── pages/            # Routed page components (lazy-loaded)
├── services/         # Injectable services
├── store/            # NgRx signal stores
├── interceptors/     # HTTP interceptors
├── pipes/            # Custom pipes
├── directives/       # Custom directives
└── models/           # TypeScript interfaces
```

## Resources

[Angular](https://angular.dev/) | [Signals](https://angular.dev/guide/signals) | [NgRx SignalStore](https://ngrx.io/guide/signals) | [Material](https://material.angular.io/) | [SSR](https://angular.dev/guide/ssr) | [i18n](https://angular.dev/guide/i18n)
