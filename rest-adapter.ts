
Stil in progress!!!! 

import type {
    Adapter,
    AdapterUser,
    AdapterAccount,
    VerificationToken,
    AdapterSession,
} from "@auth/core/adapters"
import axios from 'axios';

export function mapExpiresAt(account: any): any {
    const expires_at: number = parseInt(account.expires_at)
    return {
        ...account,
        expires_at,
    }
}

export type Routes = {
    createUser?: string;
    updateUser?: string;
    deleteUser?: string;
    getUser?: string;
    getUserByEmail?: string;
    getUserByAccount?: string;
    linkAccount?: string;
    unlinkAccount?: string;
    createSession?: string;
    updateSession?: string;
    deleteSession?: string;
    getSessionAndUser?: string;
    createVerificationToken?: string;
    useVerificationToken?: string;
};
  
export default function RestAdapter(
    backendUrl: string = 'http://0.0.0.0:8000',
    routes: Routes = {
        createUser: '/users',
        updateUser: '/users',
        deleteUser: '/users',
        getUser: '/users',
        getUserByEmail: '/users/emails',
        getUserByAccount: '/users/accounts',
        linkAccount: '/users/accounts',
        unlinkAccount: '/users/accounts',
        createSession: '/users/sessions',
        updateSession: '/users/sessions',
        deleteSession: '/users/sessions',
        getSessionAndUser: '/users/sessions',
        createVerificationToken: '/users/verification',
        useVerificationToken: '/users/verification/use'
    }

): Adapter {
    let client = axios.create({
        baseURL: `${backendUrl}/auth`,
        headers: {
          'Content-Type': 'application/json',
          'x-auth-secret': process.env.NEXTAUTH_SECRET
        }
    });

    return {
        createUser: async (user: Omit<AdapterUser, 'id'>) => {
            let response = await client.post(routes.createUser!, user);
            return response.data as AdapterUser;
        },
        
        updateUser: async (user: Partial<AdapterUser> & Pick<AdapterUser, 'id'>) => {
            let response = await client.patch(routes.updateUser!, user);
            return response.data as AdapterUser;
        },
    
        deleteUser: async (id: string) => {
            await client.delete(`${routes.deleteUser!}/${id}`);
        },
        
        getUser: async (id: string) => {
            let response = await client.get(`${routes.getUser!}/${id}`);
            return response.data ? response.data as AdapterUser : null;
        },
    
        getUserByEmail: async (email: string) => {
            let response = await client.get(routes.getUserByEmail!, { params: { email } });
            return response.data ? response.data as AdapterUser : null;
        },
    
        getUserByAccount: async ({providerAccountId, provider}: Pick<AdapterAccount, 'provider' | 'providerAccountId'>) => {
            let response = await client.get(`${routes.getUserByAccount!}/${provider}/${providerAccountId}`);
            return response.data ? response.data as AdapterUser: null;
        },
    
        linkAccount: async (account: AdapterAccount) => {
            let response = await client.post(routes.linkAccount!, account);
            return mapExpiresAt(response.data) as AdapterAccount;
        },
    
        unlinkAccount: async (account: Pick<AdapterAccount, 'provider' | 'providerAccountId'>) => {
            await client.delete(`${routes.unlinkAccount!}/${account.provider}/${account.providerAccountId}`);
        },
    
        createSession: async (session: { sessionToken: string; userId: string; expires: Date }) => {
            let response = await client.post(routes.createSession!, session);
            return response.data as AdapterSession;
        },
    
        updateSession: async (session: Partial<AdapterSession> & Pick<AdapterSession, 'sessionToken'>) => {
            let response = await client.patch(routes.updateSession!, session);
            return response.data as AdapterSession;
        },
    
        deleteSession: async (sessionToken: string) => {
            await client.delete(`${routes.deleteSession!}/${sessionToken}`);
        },
    
        getSessionAndUser: async (sessionToken: string | undefined) => {
            let session = await client.get(`${routes.getSessionAndUser!}/${sessionToken}`);
            if (!session.data) return null;
            let userID = session.data.userId;
            let user = await client.get(`${routes.getUser!}/${userID}`);
            if (!user.data) return null;
            return { session: session.data, user: user.data } as { session: AdapterSession, user: AdapterUser };
        },
    
        createVerificationToken: async (verificationToken: VerificationToken) => {
            let response = await client.post(routes.createVerificationToken!, verificationToken);
            return response.data as VerificationToken;
        },
    
        useVerificationToken: async ({ identifier, token }: { identifier: string; token: string }) => {
            let response = await client.post(routes.useVerificationToken!, { identifier, token });
            return response.data as VerificationToken;
        },
    }
}
